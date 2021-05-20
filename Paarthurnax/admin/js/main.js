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

/*UILTS*/
const uilts = {
  cqBlockParser : (cqString) => {
    //CQType
    const typeReg = /\[CQ:(.+?),/.exec(cqString);
    const cqType = typeReg && typeReg[1];
    // propetys
    const propetyRegs = [...cqString.matchAll(/([a-zA-Z]+)=(.+?)[\]\,]/g)];
    const propetys = propetyRegs.map(([raw, key, value])=> ({key, value})).reduce((acc, {key, value})=>{
      acc[key] = value;
      return acc;
    }, {})
    
    return {
      cqType, ...propetys
    }
  },
  cqParser : (cqString) => {
    return cqString.replace(/\[CQ:.+?\]/, (match)=>{
      const cq = uilts.cqBlockParser(match);
      const { cqType } = cq;
      switch( cqType ){
        case 'music':
          return `MUSIC:${cq.type}${cq.id}`
        case 'at':
          return `@${cq.qq}`
        case 'image': 
          return `IMGAE:${cq.file}`
        default:
          return match
      }
    })
  },
  randString : (targetLenght = 32) => {
    const stringCollection =  "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz123456780-";
    const stringLength = stringCollection.length;
    return Array(targetLenght).fill(1).reduce((acc)=>{
      return acc+= stringCollection.charAt(Math.floor(Math.random() * stringLength))
    },'')
  }
}

/*VUE CODE*/
const app = Vue.createApp({});
app.directive('ripple', primevue.ripple);// custom directive for ripper
const { ref, reactive, watch, onMounted, nextTick }  = Vue; 
app.component('message-box', {
  setup(){
    const {messageType} = Enum
    const messageQueue = reactive([]);
    const visibleLeft = ref(true);
    const visibleConfig = ref(false);
    const message = reactive({
      time: '',
      self_id: 10001,
      self_name: "老帕",
      message_type: messageType.GROUP,
      sub_type: '',
      message_id: '12345',
      user_id: 0,
      message: '',
      raw_message: '',
      font: '',
      nickname: 'TestAccount',
      group_id: 12312,
      anonymous:'',
    }) 


    const sendMessage = (messageContent) => {
      message.message = messageContent;
      message.time = Date.now();
      message.message_id = uilts.randString(16);
      messageQueue.push({
        sender_id: message.user_id,
        sender_name: message.nickname,
        message: message.message,
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
      Api.whisper(PostMessage).then(({status, data})=>{
        if(status === 200) {
          const { reply, at_sender } = data;
          messageQueue.push({
            sender_id: message.self_id,
            sender_name: message.self_name,
            message: uilts.cqParser(reply), // Need to parser cqCode.
          })
        } 
      }) 
    }

    const updateUser = ({id, name}) => {
      message.user_id = id;
      message.nickname = name;
    }
    // true for group, false for private
    const updateMode = (modeBool) => {
      const { GROUP, PRIVATE } = messageType;
      message.message_type = modeBool ? GROUP : PRIVATE
    } 
    const updateGroup = ({id, anonymous}) => {
      message.group_id = id;
      message.anonymous = anonymous;
    }
    const openConfig = () => {
      visibleConfig.value = !visibleConfig.value;
    }
    return {
      message,
      sendMessage,
      updateUser,
      updateMode,
      updateGroup,
      messageQueue,
      visibleLeft,
      visibleConfig,
      openConfig,
    }
  },

  template: `
    <div class="messageContainer">
        <message-window
          :messages="messageQueue"
          :type="message.message_type"
          :group="message.group_id"
          :nickname="message.nickname"
        />
        <message-input
          @open="openConfig($event)"
          @send="sendMessage($event)"
        />
        <div :class="{messageConfig: true, configHide: !visibleConfig}"> 
          <message-config
            @update:user="updateUser($event)"
            @update:mode="updateMode($event)"
            @update:group="updateGroup($event)"
          />
        </div>
    </div>
    `
})

app.component('message-window', {
  props: ["messages", "group", "nickname", "type"],
  setup(props) {
    const { messages } = props
    const messageWindowRef = ref(null)

    onMounted(() => {
      watch(messages, async ()=>{
        await nextTick();
        messageWindowRef.value.scrollTo(0, messageWindowRef.value.scrollHeight);
      })
    })

    return {
      messageWindowRef
    }
  },
  template: `
    <div ref="messageWindowRef" class="messageWindow">
      <div style="font-size: 24px; font-weight: 600; margin-bottom: 24px">Group:{{group}} | NickName:{{nickname}}</div>
      <message
        v-for="(message, index) in messages"
        :key="index"
        :sender="message.sender_name"
        :senderId="message.sender_id"
        :content="message.message"
      />
    </div>
    `
})


app.component('message', {
  props: ["sender","content", "senderId"],
  components: {
    'p-avatar': primevue.avatar,
  },
  setup(props) {
    const now = () => {
      return dayjs().format("HH:MM:ss")
    }
    return {
      now
    }
  },
  template: `
    <div class="messageContent">
      <div class="messageContentUser">
        <p-avatar 
          size="large"
          shape="circle"
          :label="sender[0]"
        />
        <div class="messageContentName">{{sender}}</div>
        <div class="messageContentTime">{{now()}}</div>
      </div>
      <pre class="messageContentInfo">{{content}}</pre>
    </div>
    `
})

app.component('message-input', {
  setup(props, {emit}){
    const message = ref('');
    const send = () => {
      emit('send', message.value)
    }
    const openConfig = () => {
      emit('open')
    }
    return {
      message,
      send,
      openConfig
    }
  },
  components: {
    'p-inputtext': primevue.inputtext,
    'p-button': primevue.button
  },
  template: `
    <div class="messageInput">
      <p-inputtext v-model="message" class="messageInputer"/>
      <div class="messageSend"><p-button @click="send()"  label="SEND"/></div>
      <div class="messageSend"><p-button @click="openConfig()" icon="pi pi-plus" class="p-button-rounded"/></div>
    </div>
    `
})

app.component('message-config', {
  components: {
    'p-inputtext': primevue.inputtext,
    'p-button': primevue.button,
    'p-togglebutton': primevue.togglebutton,
    'p-inputswitch': primevue.inputswitch, 
    'p-avatar': primevue.avatar,
  },
  setup(props, {emit}) {
    const userList = reactive([{
      id: '12345',
      name: 'TestAccount',
      hash: '$fadf'
    }]);
    const isGroupMode = ref(true);
    const selectedUserHash = ref("$fadf");
    const groupConfig = reactive({
      id: '12312',
      anonymous: false,
    })
    const inputUser = reactive({
      id: '',
      name: '',
    })

    watch(isGroupMode, ()=>{
      emit('update:mode', isGroupMode.value)
      groupConfig.id = '';
      groupConfig.anonymous = '';
    })

    watch(groupConfig, ()=> {
      emit('update:group', groupConfig)
    })

    const addUser = () => {
      userList.push({...inputUser, hash: uilts.randString(16)});
    }
    const setUser = (id, name, hash) => {
      selectedUserHash.value = hash;
      emit('update:user', {id, name})
    }
    const removeUser = (hash,ev) => {
      userList.splice(0 , +Infinity, ...userList.filter(e=>e.hash !== hash))
      ev.preventDefault()
    }
    return {
      userList,
      inputUser,
      isGroupMode,
      groupConfig,
      addUser,
      setUser,
      selectedUserHash,
      removeUser
    }
  },

  template:`
    <div>
      <div class="messageConfigTitle">Message Type</div>
      <div class="messageGroupConfig">
        <p-togglebutton v-model="isGroupMode" onLabel="Group" offLabel="Private"/>
        <div class="messageGroupInline">
          <div class="messageGroupConfigWarp">
            <div class="messageGroupConfigLabel">Group Id</div>
            <p-inputtext :disabled="!isGroupMode" v-model="groupConfig.id" />
          </div>
          <div class="messageGroupConfigWarp" style="margin-left: 8px">
            <div class="messageGroupConfigLabel">Anonymous</div>
            <p-inputswitch :disabled="!isGroupMode" v-model="groupConfig.anonymous"/>
          </div>
        </div>
      </div>
      <div class="messageConfigTitle">User Config</div>
      <div class="messageConfigUserWarp">
        <div v-for="user in userList" @click="setUser(user.id, user.name, user.hash)" :class="{messageConfigUserBlock: true, messageConfigUserBlockActive: user.hash === selectedUserHash}">
          <p-avatar 
            size="large"
            shape="circle"
            :label="user.name[0]"
            class="messageConfigUserAvatar"  
          />
          <div style="font-size: 16px;align-self: end;">{{user.name}}</div>
          <div style="font-size: 12px; color: #9c9c9c;align-self: start">{{user.id}}</div>
          <div class="messageConfigUserHander">
            <p-button icon="pi pi-times" class="p-button-rounded p-button-danger p-button-sm" @click="removeUser(user.hash, $event)"/>
          </div>
        </div>
      <div class="messageConfigUserBlock">
          <p-avatar 
            size="large"
            shape="circle"
            :label="inputUser.name? inputUser.name[0] : ''"
            class="messageConfigUserAvatar"  
          />
        <p-inputtext class="p-inputtext-sm messageConfigUserInput" v-model="inputUser.name"/>
        <div class="messageConfigUserHander">
          <p-button @click="addUser()" icon="pi pi-plus" class="p-button-rounded p-button-sm"/>
        </div>
        <p-inputtext class="p-inputtext-sm messageConfigUserInput" v-model="inputUser.id"/>
      </div>
      </div>
      
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
    app.mount('#app');

    /* Togger */
    $(".openChat").click(()=>{
      $(".chat").toggleClass("hide")
    })
});