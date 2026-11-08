from django import template

register = template.Library()

@register.filter
def format_duration(time_str):
    """
    Convert HH:MM:SS format to human-readable "X hours Y minutes" format.
    
    Example:
      "2:45:00" -> "2 hours 45 minutes"
      "0:30:00" -> "30 minutes"
      "1:00:00" -> "1 hour"
    """
    if not time_str:
        return "None"
    
    try:
        parts = str(time_str).split(':')
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        
        result = []
        
        if hours > 0:
            result.append(f"{hours} hour{'s' if hours > 1 else ''}")
        
        if minutes > 0:
            result.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        
        return " ".join(result) if result else "None"
    except (IndexError, ValueError):
        return time_str
