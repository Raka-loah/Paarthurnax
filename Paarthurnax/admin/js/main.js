$(document).ready(function(){

    $.ajax({url:"admin/settings", cache: false})
    .done(function(result){
      $("#bot-command").empty();
      $.each(result.bot_commands, function(k, v){
        var plugin = k;
        $.each(v, function(k, v){
          row = $(`<tr data-plugin="${plugin}"  id="${k}">
            <td title="${v[0]}"><input type="text" class="form-control" value="${v[1]}"></td>
            <td><div class="form-check form-check-inline"><input class="form-check-input check" type="checkbox" value="${v[2]}" ${v[2]?'checked':''}></div></td>
            <td><input type="text" class="form-control" value="${v[3].join(' ')}"></td>
            <td><input type="number" class="form-control" min="0" value="${v[4]}"></td>
            <td><div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" value="${v[5]}" ${v[5]?'checked':''}></div></td>
            <td><div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" value="${v[6]}" ${v[6]?'checked':''}></div></td>
            <td><div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" value="${v[7]}" ${v[7]?'checked':''}></div></td>
            <td><div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" value="${v[8]}" ${v[8]?'checked':''}></div></td>
            <td><input type="number" class="form-control" min="0" value="${v[9]}"></td>
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

});