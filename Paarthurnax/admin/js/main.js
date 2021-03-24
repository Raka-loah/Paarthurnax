/* API */
const Enum = {
  postType: {
    "MESSAGE": 'message',
    "NOTICE": 'notice',
    "REQUEST": 'request',
    "META": 'meta_event',
    "ERROR": 'error',
  },
  messageType: {
    "PRIVATE":'private',
    "GROUP":'group'
  },
  sex: {
    "MALE": 'male',
    "FEMALE": 'female',
    "UNKNOWN": 'unknown',
  },
  privateSubType: {
    "FRIEND": 'friend',
    "GROUP":'group',
    "OTHER":'other',
  },
  groupSubType: {
    "NORMAL":'normal',
    "ANONYMOUS":'anonymous',
    "NOTICE":'notice',
  }
}
class commonEvent {
  constructor (msg){
    this.time = msg.time || Date.now();
    this.self_id = msg.self_id;
    this.post_type = msg.post_type;
  }
}

class ErrorEvent extends commonEvent{
  constructor(msg){
    super(msg);
    this.time = msg.time || Date.now();
    this.post_type = Enum.postType.ERROR;
    this.self_id = 0;
    this.error_type = msg.error_type;
    this.errorMsg = msg.errorMsg;
  }
}
class Sender {
  constructor(msg){
    this.user_id = msg.user_id;
    this.nickname = msg.nickname;
    this.sex = msg.sex || "";
    this.age = msg.age || "";
    this.card = msg.card || "";
    this.area= msg.area || ""
    this.level=msg.level || "";
    this.role=msg.role || "";
    this.title=msg.title || "";
  }
}

class commonMessage extends commonEvent {
  constructor (msg){
    super(msg);
    this.post_type = Enum.postType.MESSAGE;
    this.message_type = msg.message_type;
    this.sub_type=msg.sub_type
    this.message_id=msg.message_id
    this.user_id=msg.user_id
    this.message=msg.message
    this.raw_message=msg.raw_message
    this.font=msg.font
    this.sender=new Sender(msg.sender);
  }
}

class PrivateMessage extends commonMessage {
  constructor(msg){
    super(msg);
    this.message_type = Enum.messageType.PRIVATE;
  }
}
class GroupMessage extends commonMessage {
  constructor(msg){
    super(msg);
    this.message_type = Enum.messageType.GROUP;
    this.group_id = msg.group_id;
    this.anonymous = msg.anonymous;
    this.sub_type = msg.sub_type;
  }
}


const Api = {
  whisper : (richMessage) => 
    axios.post('/whisper',richMessage)
}



/*VUE CODE*/
const app = Vue.createApp({});
const { ref, reactive }  = Vue; 
app.component('message-box', {
  setup(){
    const {messageType} = Enum
    const messageId = ref(0)
    const messageQueue = reactive([]);
    const message = reactive({
      time: '',
      self_id: 10001,
      message_type: messageType.GROUP,
      sub_type: '',
      message_id: messageId.value,
      user_id: 10002,
      message: '',
      raw_message: '',
      font: '',
      nickname: '',
      group_id: '',
      anonymous:'',
    }) 
    const sendMessage = () => {
      messageQueue.push({
        sender_id: message.user_id,
        sender_name: message.nickname,
        message: message.message
      })
      const PostMessage = message.message_type === messageType.GROUP ?  new GroupMessage({
        ...message,
        sender:{
          user_id: message.user_id,
          nickname: message.nickname
        }}) : new PrivateMessage({
        ...message,
        sender:{
          user_id: message.user_id,
          nickname: message.nickname
        }
      })
      Api.whisper(PostMessage).then(res=>{
        console.log(res)
      }) 
    }
    const onChange = ({field, value}) => {
      message[field] = value ;
    }
    return {
      message,
      sendMessage,
      onChange
    }
  },

  template: `
    <div>
      <message-window/>
      <message-input
        @update="onChange($event)"
        @send="sendMessage()"
      />
    </div>
    `
})

app.component('message-window', {
  setup() {
    return {
      sender: 0,
      content: 0
    }
  },
  template: `
    <div>
      <message
        :sender="sender"
        :content="content"
      />
    </div>
    `
})


app.component('message', {
  props: ["sender" ,"content"],
  template: `
    <div>
      {{sender}}
      {{content}}
    </div>
    `
})

app.component('message-input', {
  setup(props, {emit}){
    const update = (field, value) => {
      emit('update', {
        field,
        value,
      })
    }
    const send = () => {
      emit('send')
    }
    return {
      update,
      send
    }
  },
  template: `
    <div>
      <input @input="update('message',$event.target.value)" />
      <button @click="send()" >SEND</button>
    </div>
    `
})


$(document).ready(function(){

    $.ajax({url:"admin/settings", cache: false})
    .done(function(result){
      $("#bot-command").empty();
      $.each(result.bot_commands, function(k, v){
        var plugin = k;
        $.each(v, function(k, v){
          row = $(`<tr data-plugin="${plugin}"  id="${k}">
            <td title="${v[0]}"><input type="text" class="form-control" value="${v[1]}"></td>
            <td><div title="白名单" class="form-check form-check-inline"><input class="form-check-input check" type="checkbox" value="${v[2]}" ${v[2]?'checked':''}></div></td>
            <td><input title="群号" type="text" class="form-control" value="${v[3].join(' ')}"></td>
            <td><input title="CD" type="number" class="form-control" min="0" value="${v[4]}"></td>
            <td><div title="用户输入" class="form-check form-check-inline"><input class="form-check-input" type="checkbox" value="${v[5]}" ${v[5]?'checked':''}></div></td>
            <td><div title="正则" class="form-check form-check-inline"><input class="form-check-input" type="checkbox" value="${v[6]}" ${v[6]?'checked':''}></div></td>
            <td><div title="附加" class="form-check form-check-inline"><input class="form-check-input" type="checkbox" value="${v[7]}" ${v[7]?'checked':''}></div></td>
            <td><div title="启用" class="form-check form-check-inline"><input class="form-check-input" type="checkbox" value="${v[8]}" ${v[8]?'checked':''}></div></td>
            <td><input title="优先级" type="number" class="form-control" min="0" value="${v[9]}"></td>
            </tr>`);
          $("#bot-command").append(row);
        });
      });
  
      $("#alert-functions").empty();
      $.each(result.alert_functions, function(k, v){
        var plugin = k;
        $.each(v, function(k, v){
          row = $(`<tr data-plugin="${plugin}"  id="${k}">
            <td title="${v[0]}">${k}</td>
            <td><input type="number" class="form-control" min="0" max="59" value="${v[1]}"></td>
            <td><div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" value="${v[2]}" ${v[2]?'checked':''}></div></td>
            </tr>`);
          $("#alert-functions").append(row);
        });
      });
  
      $("#preprocessors").empty();
      $.each(result.preprocessors, function(k, v){
        var plugin = k;
        $.each(v, function(k, v){
          row = $(`<tr data-plugin="${plugin}"  id="${k}">
            <td title="${v[0]}">${k.replace(plugin, "")}</td>
            <td><div class="form-check form-check-inline"><input class="form-check-input check" type="checkbox" value="${v[1]}" ${v[1]?'checked':''}></div></td>
            <td><input type="text" class="form-control" value="${v[2].join(' ')}"></td>
            <td><div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" value="${v[3]}" ${v[3]?'checked':''}></div></td>
            <td><input type="number" class="form-control" min="0" value="${v[4]}"></td>
            </tr>`);
          $("#preprocessors").append(row);
        });
      });
  
      $("#postprocessors").empty();
      $.each(result.postprocessors, function(k, v){
        var plugin = k;
        $.each(v, function(k, v){
          row = $(`<tr data-plugin="${plugin}"  id="${k}">
            <td title="${v[0]}">${k.replace(plugin, "")}</td>
            <td><div class="form-check form-check-inline"><input class="form-check-input check" type="checkbox" value="${v[1]}" ${v[1]?'checked':''}></div></td>
            <td><input type="text" class="form-control" value="${v[2].join(' ')}"></td>
            <td><div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" value="${v[3]}" ${v[3]?'checked':''}></div></td>
            <td><input type="number" class="form-control" min="0" value="${v[4]}"></td>
            </tr>`);
          $("#postprocessors").append(row);
        });
      });
  
      $("input.check[type=checkbox]").change(function(){
        $(this).attr("value", (Number(this.checked)));
      });
  
      $("input[type=checkbox]:not(.check)").change(function(){
        $(this).attr("value", this.checked);
      });
    });
  
    $("#save").click(function(event) {
      event.preventDefault();
      var settings = {
        "alert_functions": {},
        "bot_commands": {},
        "preprocessors": {},
        "postprocessors": {}
      };
  
      $("#bot-command > tr").each(function(index, tr){
        var plugin = $(tr).attr("data-plugin");
        
        if (!(plugin in settings["bot_commands"])) {
          settings["bot_commands"][plugin] = {};
        }
  
        var func = tr.id;
        settings["bot_commands"][plugin][func] = [];
        
        $(tr).find(":input").each(function(k, v){
          if (k == 1 || k == 3 || k == 8) {
            settings["bot_commands"][plugin][func].push(parseInt(v.value, 10));
          } else if (k == 2) {
            settings["bot_commands"][plugin][func].push(v.value.split(" "));
          } else if (k > 2 && k < 8) {
            settings["bot_commands"][plugin][func].push(v.checked);
          } else {
            settings["bot_commands"][plugin][func].push(v.value);
          }
        });
  
      });
  
      $("#alert-functions> tr").each(function(index, tr){
        var plugin = $(tr).attr("data-plugin");
        
        if (!(plugin in settings["alert_functions"])) {
          settings["alert_functions"][plugin] = {};
        }
  
        var func = tr.id;
        settings["alert_functions"][plugin][func] = [];
        
        $(tr).find(":input").each(function(k, v){
          if (k == 0) {
            settings["alert_functions"][plugin][func].push(v.value);
          } else if (k == 1) {
            settings["alert_functions"][plugin][func].push(v.checked);
          } else {
            settings["alert_functions"][plugin][func].push(v.value);
          }
        });
  
      });
  
      $("#preprocessors> tr").each(function(index, tr){
        var plugin = $(tr).attr("data-plugin");
        
        if (!(plugin in settings["preprocessors"])) {
          settings["preprocessors"][plugin] = {};
        }
  
        var func = tr.id;
        settings["preprocessors"][plugin][func] = [];
        
        $(tr).find(":input").each(function(k, v){
          if (k == 0 || k == 3) {
            settings["preprocessors"][plugin][func].push(parseInt(v.value, 10));
          } else if (k == 1) {
            settings["preprocessors"][plugin][func].push(v.value.split(" "));
          } else if (k == 2) {
            settings["preprocessors"][plugin][func].push(v.checked);
          } else {
            settings["preprocessors"][plugin][func].push(v.value);
          }
        });
  
      });
  
      $("#postprocessors> tr").each(function(index, tr){
        var plugin = $(tr).attr("data-plugin");
        
        if (!(plugin in settings["postprocessors"])) {
          settings["postprocessors"][plugin] = {};
        }
  
        var func = tr.id;
        settings["postprocessors"][plugin][func] = [];
        
        $(tr).find(":input").each(function(k, v){
          if (k == 0 || k == 3) {
            settings["postprocessors"][plugin][func].push(parseInt(v.value, 10));
          } else if (k == 1) {
            settings["postprocessors"][plugin][func].push(v.value.split(" "));
          } else if (k == 2) {
            settings["postprocessors"][plugin][func].push(v.checked);
          } else {
            settings["postprocessors"][plugin][func].push(v.value);
          }
        });
  
      });
  
      //console.log(settings);
      
      $.ajax({method: "POST", url: "admin/settings", data: JSON.stringify(settings)})
      .done(function(result){
        console.log(result);
        message = "<p>设置修改成功，返回信息：</p><p>" + result + "</p>"
        $("#modal-message").html(message);
        $("#modal").modal('show');
      })
      .fail(function(result){
        console.log(result);
        message = "<p>设置修改失败，返回信息：</p><p>" + result + "</p>"
        $("#modal-message").html(message);
        $("#modal").modal('show');
      });
      
    });

    /* VUE MOUNT */
    app.mount('#app')
});