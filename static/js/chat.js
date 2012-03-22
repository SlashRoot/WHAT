function connect()
{
  Orbited.connect(chat_event, "django", "/chat", "0");
}


chat_event = function(data) {
  var chat_box = document.getElementById('box');
  var div = window.parent.document.createElement('div');
  div.className = "event";
  div.innerHTML = data;
  chat_box.appendChild(div);
  chat_box.scrollTop = chat_box.scrollHeight;
}
