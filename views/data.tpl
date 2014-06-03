Результат выполнения: {{"УСПЕШНО" if status else "ОШИБКА"}}<br>
<table id="command_out" class="command_out">
%for key, value in data.items():
<tr class="command_out">
<td>
  {{key}}
</td>
<td>
%if type(value) == type(list()):
%  for line in value:
     {{line}}<br>
%  end
%else:
  {{value}}
%end
</td>
</tr>
%end
</table>
</form>

