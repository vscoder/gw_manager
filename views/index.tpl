<!DOCTYPE html>
<html lang="ru">
<head>
<link type="text/css" href="/static/css/gwman.css" rel="stylesheet">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Gteway manager</title>
</head>

<body>

<div id="menu">

%for form in forms:

%include('form.tpl', **form)
<hr>

%end

</div>

<div id="data">

%if defined('data'):
%    include('data.tpl', **data)
%end

</div>

</body>

</html>
