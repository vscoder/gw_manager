<div id="status">
Результат выполнения: <img src="/static/pict/{{"yes" if status else "no"}}.png" alt="{{"yes" if status else "no"}}">
</div>
<table id="command_out" class="command_out">
%if type(data) == type(list()):
%for row in data:
<tr>
%for col in row:
<td>
%if type(col) == type(list()):
%  for line in col:
     {{line}}<br>
%  end
%elif type(col) == type(bool()):
     <img src="/static/pict/{{"yes" if col else "no"}}.png" alt="{{"yes" if col else "no"}}">
%else:
  {{col}}
%end
</td>
%end
</tr>
%end
%end

%if type(data) == type(dict()):
%for key, value in data.items():
<tr>
<td>
	{{key}}
</td>
<td>
%if type(value) == type(list()):
%  for line in value:
     {{line}}<br>
%  end
%elif type(value) == type(bool()):
     <img src="/static/pict/{{"yes" if value else "no"}}.png" alt="{{"yes" if value else "no"}}">
%else:
  {{value}}
%end
</td>
</tr>
%end
%end
</table>
</form>

