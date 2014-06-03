Результат выполнения: {{"УСПЕШНО" if status else "ОШИБКА"}}<br>
<table>
%for key, value in data.items():
<tr>
	<td>
		{{key}}
	</td>
	<td>
		{{value}}
	</td>
</tr>
%end
</table>
</form>

