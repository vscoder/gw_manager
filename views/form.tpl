<form id=input_form name="{{route}}" action="/action/{{route}}" method="get">
{{caption}}<br>
<table id="form_table">
%if defined('serversfile'):
%with open(serversfile, 'r') as f:
%servers = f.readlines()
%end
<tr>
	<td>
		Маршрутизатор
	</td>
	<td id=control_col>
		<select name="rpcserver">
%for server in servers:
			<option>{{server}}</option>
%end
		</select>
	</td>
</tr>
%end
%for (name, descr) in fields:
<tr>
	<td>
		{{descr}}
	</td>
	<td id=control_col>
		<input name="{{name}}" type="text">
	</td>
</tr>
%end
<tr>
	<td colspan=2 align=right>
		<input type="submit" value="{{button}}">
	</td>
<tr>
</table>
</form>

