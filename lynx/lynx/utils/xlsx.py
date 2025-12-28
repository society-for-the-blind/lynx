from typing import Dict, List, NamedTuple, Optional, TypeAlias
import zipfile
from io import BytesIO
from lxml import etree

from .. import kitchen_sink as lks

class WorkBookArchiveFilepath(NamedTuple):
    """
    Represents the path of a file in the XLSX archive (e.g., 'xl/worksheets/sheet1.xml')
    """
    rel_path: str

class WorkBookArchiveFileBytes(NamedTuple):
    """
    Represents the raw bytes of a file in the XLSX archive.
    """
    bytes: bytes

class SheetTree(NamedTuple):
    """
    Represents the parsed (L)XML tree of a worksheet.
    """
    lxml_tree: etree._Element

class RowTree(NamedTuple):
    """
    Represents the parsed (L)XML tree of a worksheet row.
    """
    lxml_tree: etree._Element

class CellTree(NamedTuple):
    """
    Represents the parsed (L)XML tree of a worksheet row.
    """
    lxml_tree: etree._Element

rId: TypeAlias = str

class SheetInfo(NamedTuple):
    sheet_name: str
    rId: rId
    path: WorkBookArchiveFilepath
    sheet_tree: SheetTree

Sheets: TypeAlias = List[SheetInfo]

# This structure will represent each file in the XLSX archive via
# its path mapped to its raw bytes.
WorkBookArchiveFilepathsWithBytes: TypeAlias = \
    Dict[WorkBookArchiveFilepath, WorkBookArchiveFileBytes]
# SheetMeta: TypeAlias = Dict[str, str]

class Cell(NamedTuple):
    """
    Represents a cell in a worksheet by its column, row, and full reference.
    """
    column: str
    row: int

    @property
    def ref(self) -> str:
        """Returns the full cell reference as a string."""
        return f"{self.column}{self.row}"

    @property
    def column_letter_to_index(self) -> int:
        """
        Convert an Excel column letter(s) to a 1-based column index.

        Examples:
          'A' -> 1
          'Z' -> 26
          'AA' -> 27
        """
        self.column = self.column.upper()
        index = 0
        for char in self.column:
            index = index * 26 + (ord(char) - ord('A') + 1)
        return index

    @property
    def index_to_column_letter(index: int) -> str:
        """
        Convert a 1-based column index to Excel column letters.

        Args:
          idx: integer index (1-based).

        Returns:
          Column letters string (e.g. 1 -> 'A').
        """
        letters = []
        while idx:
            idx, rem = divmod(idx - 1, 26)
            letters.append(chr(rem + ord('A')))
        return ''.join(reversed(letters))


NS = {
    'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'rel':  'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}

def load_xlsx_to_memory(xlsx_path: str) -> WorkBookArchiveFilepathsWithBytes:
    """
    Read an .xlsx file (which is a ZIP archive) into memory.

    Args:
      xlsx_path: file system path to the .xlsx file on disk.

    Returns:
      A dict mapping archive member name -> raw bytes. Example keys:
      'xl/workbook.xml', 'xl/worksheets/sheet1.xml', '[Content_Types].xml', etc.

    Notes:
      - This function does not attempt to interpret any XML; it simply reads the ZIP contents.
      - Useful when you want to modify only specific XML parts and write back a new .xlsx
        without touching unknown extensions.
    """
    with zipfile.ZipFile(xlsx_path, 'r') as zip_iterator:
        return { WorkBookArchiveFilepath(rel_path=name):
                    WorkBookArchiveFileBytes(bytes=zip_iterator.read(name))
                    for name in zip_iterator.namelist()
               }

def write_memory_to_xlsx(wba_files: WorkBookArchiveFilepathsWithBytes, out_path: str) -> None:
    """
    Persist an in-memory files dict back to an .xlsx file.

    Args:
      wba_files: dict of archive_name -> bytes (same shape as produced by load_xlsx_to_memory).
      out_path: destination path for the resulting .xlsx file.

    Behavior:
      - Writes all provided members into a ZIP file using ZIP_DEFLATED compression.
      - Overwrites out_path if it exists.
    """
    with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_file:
        for wbaf_path, wbaf_bytes in wba_files.items():
            zip_file.writestr(wbaf_path.rel_path, wbaf_bytes.bytes)

def parse_XML(maybe_xml_bytes: bytes) -> etree._Element:
    """
    Parse XML bytes into an lxml Element.

    Args:
      wbaf_bytes: XML content bytes (UTF-8).

    Returns:
      lxml.etree._Element root element.

    Note:
      - This helper centralizes XML parsing and is used by higher level helpers.

    WARNING: This will blow up if the raw bytes are not read from a valid XML file!
            An XLSX archive may contain non-XML files (e.g., `xl/printerSettings`
            contains raw binaries) - but it *should* blow up, because it will only
            called on a fixed input (i.e., the DOR template), so it should always
            work once deployed.
    """
    return etree.fromstring(maybe_xml_bytes)

def serialize_lxml_tree(el: etree._Element) -> bytes:
    """
    Serialize an lxml Element back to bytes suitable for inclusion in the .xlsx archive.

    Args:
      el: parsed XML element.

    Returns:
      bytes with XML declaration, encoded as UTF-8.
    """
    return etree.tostring(el, xml_declaration=True, encoding='UTF-8', standalone=False)

def get_rId_to_sheet_name_mapping(wba_files: WorkBookArchiveFilepathsWithBytes) -> Dict[rId, str]:

    workbook_xml_path = WorkBookArchiveFilepath(rel_path='xl/workbook.xml')
    workbook_xml_bytes = wba_files[workbook_xml_path]
    workbook_xml_lxml = parse_XML(workbook_xml_bytes.bytes)

    # <sheets>
    # 	<sheet name="7-OB Report" sheetId="7" r:id="rId1"/>
    # 	<sheet name="Instructions" sheetId="6" r:id="rId2"/>
    # 	<sheet name="PART II-PROGRAM STAFFING" sheetId="5" r:id="rId3"/>
    # 	<sheet name="PART III-DEMOGRAPHICS" sheetId="1" r:id="rId4"/>
    # 	<sheet name="PART IV-V-SERVICES AND OUTCOMES" sheetId="2" r:id="rId5"/>
    # 	<sheet name="Counties" sheetId="8" r:id="rId6"/>
    # 	<sheet name="Data" sheetId="9" r:id="rId7"/>
    # </sheets>
    sheets_lxml = workbook_xml_lxml.find('main:sheets', namespaces=NS)
    # Build a mapping of relationship-id (r:id) -> display name
    rId_to_sheet_name: Dict[rId, str] = {}
    for sheet_lxml in sheets_lxml.findall('main:sheet', namespaces=NS):
      sheet_name = sheet_lxml.get('name')
      rid = sheet_lxml.get('{%s}id' % NS['rel']) or sheet_lxml.get('r:id') or sheet_lxml.get('id')
      if sheet_name and rid:
        rId_to_sheet_name[rid] = sheet_name

    return rId_to_sheet_name

def get_sheets(wba_files: WorkBookArchiveFilepathsWithBytes) -> Sheets:
    """
    Inspect `xl/_rels/workbook.xml.rels` and return `SheetInfo` records for each worksheet.

    It finds Relationship entries whose Type is the worksheet type and returns a
    SheetInfo per worksheet with:
      - rId: relationship id (e.g. "rId3")
      - path: WorkBookArchiveFilepath(rel_path='xl/worksheets/sheet3.xml')
      - bytes: WorkBookArchiveFileBytes for the worksheet XML (from `wba_files`)

    """
    workbook_xml_rels_path = WorkBookArchiveFilepath(rel_path='xl/_rels/workbook.xml.rels')
    workbook_xml_rels_bytes = wba_files[workbook_xml_rels_path]

    # <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    # <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    # 	<Relationship Id="rId8" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
    # 	<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/>
    # 	<Relationship Id="rId11" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sheetMetadata" Target="metadata.xml"/>
    #   ...
    # </Relationships>
    rels_lxml = parse_XML(workbook_xml_rels_bytes.bytes)

    sheets: Sheets = []

    rId_to_sheet_name_dict = get_rId_to_sheet_name_mapping(wba_files)

    for rel in rels_lxml.findall('.//'):
        rel_rid = rel.get('Id')
        sheet_name = rId_to_sheet_name_dict.get(rel_rid)
        # skip non-worksheet relationships
        if sheet_name is None:
            continue
        target = rel.get('Target')  # typically 'worksheets/sheetN.xml'
        sheet_rel_path_str = 'xl/' + target.lstrip('/')
        sheet_wbaf_path = WorkBookArchiveFilepath(rel_path=sheet_rel_path_str)
        sheet_wbaf_bytes = wba_files.get(sheet_wbaf_path)
        sheet_info = SheetInfo(
            rId=rel_rid,
            sheet_name=sheet_name,
            # TODO validate: wba_files[path.rel_path] == serialize_lxml_tree(sheet_tree.lxml_tree)
            path=sheet_wbaf_path,
            sheet_tree=SheetTree(lxml_tree=parse_XML(sheet_wbaf_bytes.bytes))
        )
        sheets.append(sheet_info)

    return sheets

# This refers to upserting a <c> element's <v> element
def set_cell(sheet_tree: SheetTree, cell: Cell, value: str) -> SheetTree:
    sheet_tree_lxml = sheet_tree.lxml_tree

    # Ensure that the <sheetData> element exists
    sheet_data = sheet_tree_lxml.find('main:sheetData', namespaces=NS)
    if sheet_data is None:
        raise ValueError("worksheet is missing <sheetData>; not a valid template")
    # Ensure that the row that `cell` refers to exists
    row_num = str(cell.row)
    row_lxml = sheet_data.find(f"main:row[@r='{row_num}']", namespaces=NS)
    if row_lxml is None:
        # row_lxml = etree.SubElement(sheet_data, '{%s}row' % NS['main'])
        # row_lxml.set('r', cell.ref)
        raise ValueError(f"worksheet is missing row {row_num}; is template valid?")

    cell_lxml = sheet_tree_lxml.xpath(f"//main:c[@r='{cell.ref}']", namespaces=NS)[0]

    if cell_lxml is None:
        # cell_lxml = etree.SubElement(row_lxml, '{%s}c' % NS['main'])
        # cell_lxml.set('r', cell.ref)
        raise ValueError(f"worksheet is missing cell {cell.ref}; is template valid?")
    if cell_lxml.get('t') == 's':
        raise ValueError(f"cell {cell.ref} uses sharedStrings (t='s')")
    if len(cell_lxml) > 0:
        raise ValueError(f"cell {cell.ref} has unexpected child elements. Check if this cell should be filled out.")

    cell_lxml.set('t', 'inlineStr')
    # Create the nested structure for `inlineStr`: <is><t>...</t></is>
    is_element_lxml = etree.SubElement(cell_lxml, f"{{{NS['main']}}}is")
    t_element_lxml = etree.SubElement(is_element_lxml, f"{{{NS['main']}}}t")
    t_element_lxml.text = value

    return SheetTree(lxml_tree=sheet_tree_lxml)

def set_column(sheet_tree: SheetTree, start_cell: Cell, values: List[str]) -> SheetTree:
    """
    Write a vertical column of values into a worksheet, starting at start_cell.

    Args:
      sheet_tree: parsed worksheet XML element.
      start_cell: e.g. 'B4' - the first cell to write into.
      values: list of values (any objects will be converted to str).
      as_inline: whether to write values as inlineStr. (default True)

    Behavior:
      - Iterates values and writes them downwards in the same column.
      - Uses set_cell for each cell (so preserves worksheet-level unknown parts).
    """
    for str in values:
        sheet_tree = set_cell(sheet_tree, start_cell, str)
        start_cell = Cell(column=start_cell.column, row=start_cell.row + 1)
    return sheet_tree

def write_column(
      wba_files: WorkBookArchiveFilepathsWithBytes,
      sheet_rid: rId,
      start_cell: str,
      values: List[str]
    ) -> WorkBookArchiveFilepathsWithBytes:
    """
    Convenience wrapper that writes a column into a named worksheet inside the in-memory wba_files dict.

    Args:
      wba_files: in-memory xlsx archive dict.
      sheet: display name of the worksheet (e.g. 'Sheet1').
      start_cell: first cell to write into (e.g. 'B4').
      values: list of values to write downwards.

    Raises:
      ValueError if sheet is not present in the workbook.
    """
    sheets = get_sheets(wba_files)
    matched_sheet_info = next((s for s in sheets if s.rId == sheet_rid), None)
    sheet_tree = matched_sheet_info.sheet_tree
    sheet_path = matched_sheet_info.path

    sheet_tree = set_column(sheet_tree, start_cell, values)
    sheet_bytes = serialize_lxml_tree(sheet_tree.lxml_tree)
    wba_files[sheet_path] = WorkBookArchiveFileBytes(bytes=sheet_bytes)
    return wba_files

def get_sheet_path_by_name(files: WorkBookArchiveFilepathsWithBytes, sheet_name: str) -> Optional[str]:
    """
    Return the archive path for a worksheet given its display name.

    Args:
      files: in-memory xlsx archive dict.
      sheet_name: worksheet display name.

    Returns:
      The archive path (e.g. 'xl/worksheets/sheet1.xml') or None if not found.
    """
    sheets = get_sheets(files)
    match = next((s for s in sheets if s.sheet_name == sheet_name), None)
    return match['path'] if match else None

def dump_files_to_bytesio(files: WorkBookArchiveFilepathsWithBytes) -> BytesIO:
    """
    Build an .xlsx archive from the in-memory files dict and return it as a BytesIO.

    Args:
      files: in-memory xlsx archive dict.

    Returns:
      BytesIO positioned at start containing the .xlsx ZIP bytes.
    """
    bio = BytesIO()
    with zipfile.ZipFile(bio, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for name, content in files.items():
            zout.writestr(name, content)
    bio.seek(0)
    return bio

# Example:
# =================================================================
# $ python lynx/manage.py shell
# Python 3.10.9 (main, Dec  6 2022, 18:44:57) [GCC 11.3.0] on linux
# Type "help", "copyright", "credits" or "license" for more information.
# (InteractiveConsole)

# >>> import lynx.utils.xlsx as x; template = "sftb/xlsx_templates/7-OB_Report_Data_Collection_Tool_2025.xlsx"; values = ["lofa", "vmi", "balabab"]; wbaf = x.load_xlsx_to_memory(template); print(*x.get_sheets(wbaf), sep="\n");

# SheetInfo(sheet_name='PART II-PROGRAM STAFFING', rId='rId3', path=WorkBookArchiveFilepath(rel_path='xl/worksheets/sheet3.xml'), sheet_tree=SheetTree(lxml_tree=<Element {http://schemas.openxmlformats.org/spreadsheetml/2006/main}worksheet at 0x74c22a50ab40>))
# SheetInfo(sheet_name='Data', rId='rId7', path=WorkBookArchiveFilepath(rel_path='xl/worksheets/sheet7.xml'), sheet_tree=SheetTree(lxml_tree=<Element {http://schemas.openxmlformats.org/spreadsheetml/2006/main}worksheet at 0x74c22a50ac40>))
# SheetInfo(sheet_name='Instructions', rId='rId2', path=WorkBookArchiveFilepath(rel_path='xl/worksheets/sheet2.xml'), sheet_tree=SheetTree(lxml_tree=<Element {http://schemas.openxmlformats.org/spreadsheetml/2006/main}worksheet at 0x74c22a50ad40>))
# SheetInfo(sheet_name='7-OB Report', rId='rId1', path=WorkBookArchiveFilepath(rel_path='xl/worksheets/sheet1.xml'), sheet_tree=SheetTree(lxml_tree=<Element {http://schemas.openxmlformats.org/spreadsheetml/2006/main}worksheet at 0x74c22a50ae40>))
# SheetInfo(sheet_name='Counties', rId='rId6', path=WorkBookArchiveFilepath(rel_path='xl/worksheets/sheet6.xml'), sheet_tree=SheetTree(lxml_tree=<Element {http://schemas.openxmlformats.org/spreadsheetml/2006/main}worksheet at 0x74c22a50af40>))
# SheetInfo(sheet_name='PART IV-V-SERVICES AND OUTCOMES', rId='rId5', path=WorkBookArchiveFilepath(rel_path='xl/worksheets/sheet5.xml'), sheet_tree=SheetTree(lxml_tree=<Element {http://schemas.openxmlformats.org/spreadsheetml/2006/main}worksheet at 0x74c22a50b080>))
# SheetInfo(sheet_name='PART III-DEMOGRAPHICS', rId='rId4', path=WorkBookArchiveFilepath(rel_path='xl/worksheets/sheet4.xml'), sheet_tree=SheetTree(lxml_tree=<Element {http://schemas.openxmlformats.org/spreadsheetml/2006/main}worksheet at 0x74c22a50b180>))

# >>> _ = x.write_column( wba_files=wbaf, sheet_rid="rId4", start_cell=x.Cell(column='A', row=17), values=values);
# >>> x.write_memory_to_xlsx(wbaf, "/tmp/fff.xlsx")