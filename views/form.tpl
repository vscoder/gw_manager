<form name="{{route}}" action="/action/{{route}}" method="get">
{{caption}}<br>
<table>
%for (name, descr) in fields:
<tr>
	<td>
		<input name="{{name}}" type="text">
	</td>
	<td>
		{{descr}}
	</td>
</tr>
%end
<tr>
	<td colspan=2 align=center>
		<input type="submit" value="{{button}}">
	</td>
<tr>
</table>
</form>

