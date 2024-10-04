ROOT = '''
<html>
<head>
    <title>KP-MSX</title>
</head>
<body>
    <pre>

888    d8P  8888888b.       888b     d888  .d8888b. Y88b   d88P 
888   d8P   888   Y88b      8888b   d8888 d88P  Y88b Y88b d88P  
888  d8P    888    888      88888b.d88888 Y88b.       Y88o88P   
888d88K     888   d88P      888Y88888P888  "Y888b.     Y888P    
8888888b    8888888P"       888 Y888P 888     "Y88b.   d888b    
888  Y88b   888      888888 888  Y8P  888       "888  d88888b   
888   Y88b  888             888   "   888 Y88b  d88P d88P Y88b  
888    Y88b 888             888       888  "Y8888P" d88P   Y88b 
                                                                
                                                                
                                                                
    </pre>
    <p>Это <b>неофициальный</b> кинопаб для Media Station X.</p>
    <p>Чтобы этим пользоваться, введите <b><a id="host">адрес страницы</a></b> в Start Parameter (Плейлист) в настройках Media Station X</p>
    <p>Чтобы попасть в настройки Media Station X, нажмите правую цветную кнопку на пульте</p>
    <p>При возникновении проблем, вопросов, пожеланий, предложений при использовании этой версии не обращайтесь в поддержку кинопаба<p>
    <p><b>Прочитайте, что написано <a href="https://github.com/slonopot/kp-msx">здесь</a>, и следуйте инструкциям</b></p>
    <p style="display: none" id="render"><b>Эта версия может останавливаться при простое, при первом обращении сервис запустится снова через минуту. Если не грузится сразу, попробуйте еще раз.</b></p>
    
    <script>
        var host = window.location.host;
        document.getElementById('host').innerText = host;
        if (host.includes('onrender.com')) document.getElementById('render').style = '';
    </script>
</body>
</html>
'''