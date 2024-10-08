# kp-msx: серверный клиент для кинопаба для Media Station X.

# Прочитайте внимательно вот это вот: 

1. Этот проект не имеет никакого прямого отношения к кинопабу, к администрации кинопаба, к поддержке кинопаба, это просто еще один вариант сервировки. Администрация кинопаба и поддержка кинопаба не должны и не будут помогать вам с установкой и настройкой этой поделки. Не обращайтесь по этому проекту в поддержку кинопаба или в чаты кинопаба, вас будут называть обидными словами.
2. Поддержка с моей стороны оказывается только в Issues (сверху) и только по настроению. Достоверно известно, что на момент публикации все работает (с некоторыми ограничениями, о них ниже).
3. Требуемый уровень компьютерной грамотности: выше среднего. Для запуска этого проекта на своем сервере вам потребуются сам сервер, знания и умения управления сервером и какое-то базовое понимание того, что вообще происходит. При возникновении сложностей при запуске и настройке, пожалуйста, сначала обратитесь к своему знакомому, который шарит. Если у вас уже есть свой сервер под VPN, он подойдет идеально.
4. Для запуска этого проекта на render.com требуется меньше усилий, но на пути могут встретиться сложности в виде английского языка, региональных ограничений, фрода, решение которых не относится к данному проекту.
5. Предоставленные инструкции дают направление для проб и ошибок, но не гарантию работоспособности в вашем конкретном случае.
6. Это кривой незаконченный продукт, но он работает, поэтому все пожелания, конечно, приветствуются, но учитываться будут тогда, когда возникнет желание выпрямить и доделать.
7. Инвестиция в приставку типа Google Chromecast или Apple TV надежнее и проще, особенно если телевизор уже пожилой. Можно попытаться выжать из него последнее, но нужно ли...

## Что это такое и чем это отличается от всего остального

Это сервер, с которым общается телевизор, и клиент, общающийся с кинопабом. Типа прокси, но с преобразованием ответов в родной формат MSX. В данный момент основные блокировки затрагивают адреса самого кинопаба, но не видео. Если вынести общение с кинопабом туда, где он не заблокирован, и передавать переработанную информацию в MSX через заведомо рабочий канал (телевизор-сервер), то все должно работать.

В отличие от аналогов данный проект требует больше усилий для развертывания, но имеет большую устойчивость перед блокировками.

## Важно знать

Ключи доступа (токены), используемые для общения с кинопабом, хранятся в базе того пользователя, который администрирует конкретный сервер (ссылку). С токенами можно сделать не так много разного, но это все еще чувствительная информация. Если вы используете чужую ссылку, администратор этой ссылки может использовать ваш токен в каких-то там личных целях, поэтому здраво оценивайте риски использования каких попало ссылок.

Если ваш телевизор не тянет HLS4 стримы и показывает ошибку Source Not Supported или не дает переключать дорожки или отваливается при воспроизведении, в конце есть информация, как заставить работать HTTP. Если и это не помогает -- приобретайте приставку.

Очевидно, сервера в странах, где кинопаб недоступен, не подходят.

## Как пользоваться

TODO: для упрощения жизни при использовании на своем сервере надо бы добавить поддержку sqlite вместо монго.

Поставьте последний (3.12 или около того) Python так, как умеете, MongoDB (можно бесплатный Atlas, об этом далее), и дальше как-то так:

```
git clone https://github.com/slonopot/kp-msx
cd kp-msx
python3.12 -m venv venv
./venv/bin/pip install -r requirements.txt
MONGODB_URL="ссылка на монго" MSX_HOST="http://ваш айпи:1234" nohup ./venv/bin/uvicorn --host 0.0.0.0 --port 1234 api:app &
```

Если `http://{IP}:{PORT}/msx/start.json` отвечает, значит, все получилось.

В аргумент MSX вписать айпи вашего сервера и порт (1234 в вашем случае) через двоеточие, например: `1.2.3.4:1234`.

Можно кинуть на домен и прокинуть через nginx через proxy_pass. Для этого можно `--host 127.0.0.1`, `MSX_HOST="http://ваш домен"` и в конфиге сайта для nginx сделать, например, так:

```
    location /msx {
        proxy_pass http://127.0.0.1:1234;
    }
```

После `service nginx reload` должен отвечать по `https://{ваш домен}/msx/start.json`, в параметр MSX впишите ваш домен.

# Как пользоваться, если сервера нет, денег нет...

Для того, чтобы продукт заработал, нужны база данных и сервер, и их на попробовать иногда дают бесплатно.

## MongoDB Atlas

Для этого этапа потребуется VPN из-за региональных ограничений. 

После [регистрации тут](https://account.mongodb.com/account/register), подтверждения почты, прокликивания тысячи пунктов, выбора бесплатного тарифа и некоторого ожидания получится ссылка для подключения к базе вида `mongodb+srv://abcd:efgh@ijkl.mnop.mongodb.net/`. 

Если готовую ссылку найти не удалось, во вкладке Overview в разделе Cluster кнопка Connect после выбора, например, Compass покажет ссылку вида `mongodb+srv://<db_username>:<db_password>@1234.5678.mongodb.net/`, в которую нужно подставить логин и пароль. 

Создать новые логин и пароль можно во вкладке Database Access по кнопке Add New Database User: введите логин (допустим, `vasya`), пароль (можно сгенерировать, допустим, `6789`), и после нажатия Built-in Roles выберите Atlas Admin. В конце нажмите Add User и подставьте получившиеся логин и пароль в ссылку из предыдущего шага, например, так: `mongodb+srv://vasya:6789@1234.5678.mongodb.net/`.

В конце нужно разрешить подключаться к этой базе откуда угодно, для этого во вкладке Network Access нажмите Add IP Address, в Access List Entry вставьте `0.0.0.0/0` и сохраните нажатием Confirm.

## Render.com

Для этого этапа наоборот не потребуется VPN из-за фрода, насчет региональных ограничений информации нет.

После [регистрации тут](https://dashboard.render.com/register) в панели управления потребуется [создать Web Service](https://dashboard.render.com/web/new), выберите Public Git Repository и вставьте ссылку `https://github.com/slonopot/kp-msx/`, нажмите Connect. В Name вместо kp-msx впишите что-то короткое и простое на латинице, Region можно выбрать Frankfurt, Build Command должен подставиться автоматически как `pip install -r requirements.txt`, а Start Command нужно прописать как `uvicorn --host 0.0.0.0 --port 10000 api:app`. Instance Type выберите как Free, так как денег нет, в Environment Variables в NAME_OF_VARIABLE нужно вписать `MONGODB_URL`, а справа в value ссылку, полученную в предыдущем разделе, например, `mongodb+srv://abcd:efgh@ijkl.mnop.mongodb.net/`.

По нажатию Deploy Web Service либо получится все сразу, либо попросят карту. Если карту попросили -- значит, сработал фрод, можно попробовать зарегистрироваться с другого айпи, в инкогнито, либо просто дать карту, с нее ничего списать не должны.

Если все удалось, в открывшемся разделе слева сверху будет ссылка вида `https://имя.onrender.com`, в разделе Logs (справа в дате выбрать Live Tail) нужно ожидать появления `==> Running 'uvicorn --host 0.0.0.0 --port 10000 api:app'`. После того, как сервис запустился, `имя.onrender.com` начнет отвечать в браузере, можно вписать в параметр MSX и попробовать.

**Важно: в связи с бесплатностью предоставляемой услуги неиспользуемые сервисы со временем останавливаются, поэтому на следующий день при первом открытии свежий запуск займет где-то минуту. Предварительно можно потыкать ссылку в браузере, пока не начнет отвечать.**

## Дополнительные настройки

В Environment Variables настраивается следующее:

| Имя         | Описание                                                                                                                                       | Значения                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MSX_HOST    | Адрес сервера для подстановки в ссылки. Альтернативно RENDER_EXTERNAL_URL заполнится render.com автоматически                                  | `http[s]://host.domain[:port]`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| MONGODB_URL | Адрес для подключения к монго                                                                                                                  | `mongodb(+srv)://user:passw@host.domain:port`                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| PORT        | Порт, на котором будет запущен сервер, еслм запускать как `python api.py`, для uvicorn указывается отдельно. 10000 по умолчанию для render.com | `1234`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|PLAYER| Плеер, который будет показывать кино. Для HLS нужен свой, для HTTP -- свой.                                                                    | [Стандартные](https://msx.benzac.de/wiki/index.php?title=Video/Audio_Plugin#:~:text=for%20more%20information.-,Examples,-%5Bedit%5D)<br/>HTTP: `http://msx.benzac.de/plugins/html5.html` <br/>HTTP с сабами: `http://msx.benzac.de/plugins/html5x.html` <br/> HLS: `http://msx.benzac.de/plugins/hls.html` <br/><br/> Допиленные мной <br/> HTTP с кастомными сабами: `https://slonopot.github.io/msx-html5xs/html5xs.html` <br/> HLS с дорожками и сабами (по умолчанию): `https://slonopot.github.io/msx-hlsx/hlsx.html` |
|PROTOCOL| Протокол, если телек не тянет HLS4                                                                                                             | `hls4` (по умолчанию)<br/> `hls2` (то же самое, что и hls4) <br/> `hls` <br/> `http`                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|QUALITY| Качество, если протокол `http` или `hls`. Если не указано или не найдено, то максимально доступное                                             | `2160p` (4K должно быть включено в кинопабе) <br/> `1080p`, `720p`, `480p`                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

Для того, чтобы перенастроить на HLS вместо HLS4, добавьте `PROTOCOL = hls`. У HLS нет дорожек и сабов, но есть вероятность, что он хотя бы запустится.

Для того, чтобы перенастроить на HTTP вместо HLS4, делайте типа так:

|NAME_OF_VARIABLE| value                                                      |
|-|------------------------------------------------------------|
|PLAYER| `http://msx.benzac.de/plugins/html5x.html` или `https://slonopot.github.io/msx-html5xs/html5xs.html` |
|PROTOCOL| `http`                                                     |
|QUALITY| `1080p` или не указывать вообще                            |

Сабы и дорожки при таком раскладе могут заработать, могут не заработать, зависит от чуда. Сабы сломаны в обновлении, чинить лень.

Если хостите на render.com, можно создать несколько разных ссылок с разными параметрами, просто делайте новый Web Service справа сверху. Ссылку на монго можно использовать одну и ту же.