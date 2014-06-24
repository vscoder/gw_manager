<!DOCTYPE html>
<html lang="ru">
<head>
<link type="text/css" href="/static/css/gwman.css" rel="stylesheet">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
<meta http-equiv="Pragma" content="no-cache" />
<meta http-equiv="Expires" content="0" />
<title>Gteway manager</title>
</head>

<body>

<div id="menu" class="left">

%for form in forms:

%include('form.tpl', **form)

%end

</div>

<div id="data" class="right">

%if defined('data'):
%    include('data.tpl', **data)
%end

</div>

</body>

</html>
