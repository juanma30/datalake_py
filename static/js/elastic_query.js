var elastic = {

  size: 500,

  _source: ["SequenceNumber","RuleName","Protocol","SourceIP", "DestinationIP","SourceUser","@timestamp","Action","LogAction","Application","host", "Type","ActionFlags","Flags","ReceiveTime","timestamp"],

  sort: [{
    "@timestamp":{
      "order":"",
      "unmapped_type":"boolean"
    }
  }],

  filter: {
    "range": {
      "@timestamp": {
        "format":"strict_date_optional_time",
        "gte": "",
        "lte": ""
      }
    }
  },

  match: {},

  bool: {},

  query: {},

  aggs1: {
    "ciber_centros": {
      "terms": {
        "field": "RuleName.keyword",
        "size": "100"
      },
      "aggs": {
        "devices": {
          "terms": {
            "field": "SourceUser.keyword",
            "size": "1000"
          }
        }
      }
    }
  },

  aggs2: {
    "devices": {
      "cardinality": {
        "field": "SourceUser.keyword"
      }
    }
  },

  activos: {
    "size":"0",
    "aggs":{
      "ciber_centros":{
        "terms":{
          "field":"RuleName.keyword","size":"100"
        },
        "aggs":{
          "devices":{
            "terms":{
              "field":"SourceUser.keyword","size":"1000"
            }
          }
        }
      }
    },
    "query":{
      "bool":{
        "must":[],
        "filter":{
          "range":{
            "@timestamp":{
              "format":"strict_date_optional_time",
              "gte":"",
              "lte":""
            }
          }
        }
      }
    }
  },

  inactivos: {
    "size":"0",
    "aggs":{
      "ciber_centros":{
        "terms":{
          "field":"RuleName.keyword","size":"100"
        },
        "aggs":{
          "devices":{
            "terms":{
              "field":"SourceUser.keyword","size":"1000"
            }
          }
        }
      }
    },
    "query":{
      "bool":{
        "must":[],
        "filter":{
          "range":{
            "@timestamp":{
              "format":"strict_date_optional_time",
              "gte":"",
              "lte":""
            }
          }
        }
      }
    }
  },

  formatDate: function(date){
    var fecha_final = [];
    fecha = atob(date);
    fecha_tmp = fecha.split(' - ');
    for(var i in fecha_tmp){
      f = new Date(fecha_tmp[i]);
      fecha_final.push(f.toISOString());
    }
    return fecha_final;
  },

  restaDia: function(fecha,dia){
    var d = new Date(fecha);
    var tmp = new Date(d.setDate(d.getDate() - dia));
    return tmp.toISOString();
  },

  setOrderSort:function(order){
    this.sort[0]['@timestamp'].order = order;
  },

  setFilterRange:function(date){
    this.filter.range['@timestamp'].gte = date[0];
    this.filter.range['@timestamp'].lte = date[1];
  },

  setBool: function(data=false){
    if(data==false){
      this.bool['must'] = [];
    }else{
      this.bool['must'] = [data];
    }
    this.bool['filter'] = this.filter;
    this.query["query"] = {};
    this.query['query']['bool'] = {};
    this.query.query.bool = this.bool;
  },

  setQuery: function(){
    this.query["size"] = this.size;
    this.query["sort"] = this.sort;
    this.query["_source"] = this._source;
  },

  setMatch: function(data){
    if(typeof data == "object"){
      this.match = data;
    }
    this.query["query"] = {};
    this.query["query"]['match'] = this.match;
  },

  formatDataTable: function(data){
    var tmp = [];
    for(var i in data){
      tmp.push(
        [
            data[i]._source.timestamp,
            data[i]._source.host,
            data[i]._source.SourceIP,
            data[i]._source.Action,
            data[i]._source.Type,
            data[i]._source.RuleName,
            data[i]._source.SourceUser,
            '<button class="btn btn-info btn-info-ip" data-id="'+data[i]._source.SequenceNumber+'">Detalle</button>'
        ]
      );
    }
    return tmp;
  },

  setInfoTable: function(date,cc,order='desc',tabla,onsubmit=0,token=''){
    this.query = {};
    date = this.formatDate(date);
    this.setOrderSort(order);
    this.setFilterRange(date);
    this.setQuery();
    if(cc!=0) this.setBool({"match":{"RuleName.keyword":cc}});
    else this.setBool();
    console.log("QUERY: ",JSON.stringify(this.query));
    $.post("./php/elasticsh.php",{data: this.query, tabla:true, sub:onsubmit, token:token},function(rs){
      if(rs != undefined){
        var tmp = elastic.formatDataTable(rs['data']);
        tabla.fnClearTable();
        for(var i in tmp){
          tabla.fnAddData(tmp[i]);
        }
        $("#container_loader_tabla").hide();
      }
    });
  },

  modalTable: function(id_log,id_table){
    this.query = {};
    this.setMatch({"SequenceNumber":id_log});
    $.post("./php/elasticsh.php",{data: this.query, tabla:true},function(rs){
      if(rs != undefined){
        if(rs.data[0]._source != undefined){
          var tmp = rs.data[0]._source;
          var columnas = [];
          var valores = [];
          for(var i in tmp){
            if(typeof tmp[i] != 'object' && typeof tmp[i] != 'array'){
              columnas.push('<th>'+i+'</th>');
              valores.push('<td>'+tmp[i]+'</td>');
            }
          }
          var col = columnas.join('');
          var val = valores.join('');
          $("#"+id_table).html("<tr>"+col+"</tr>"+"<tr>"+val+"</tr>");
        }
      }
    });
  },

  data_activos : [],

  data_inactivos : [],

  updBarChart: function(dd,grafica){
    if(dd != undefined){
      var dataset = [{
          label: "DISPOSITIVOS",
          data: dd.totales,
          fill: false,
          backgroundColor: ["rgba(31, 168, 62, 0.2)","rgba(255, 99, 132, 0.2)"],
          borderColor: ["rgba(31, 168, 62)","rgb(255, 99, 132)"],
          borderWidth: 1
      }];
      this.addDataChart(grafica,false,dataset);
    }
  },

  addDataChart: function (chart,labels=false,dataset=false){
    if(chart != undefined){
      if(labels != false) chart.data.labels = labels;
      if(dataset !== false) chart.data.datasets = dataset;
      chart.update();
    }
  },

  getActivos_Inactivos: function(fecha,cc,grafica,onsubmit=0,token=''){
    this.query = {};
    var hoy = this.formatDate(fecha);
    this.activos.query.bool.filter.range['@timestamp'].gte = hoy[0];
    this.activos.query.bool.filter.range['@timestamp'].lte = hoy[1];
    var data = this.activos;
    if(cc != 0){
      this.activos.query.bool.must.push({"match": { "RuleName.keyword": cc }});
      this.activos['cibercentro'] = cc;
    }else{
      this.activos.query.bool.must = [];
      this.activos['cibercentro'] = undefined;
    }
    $.post("./php/elasticsh.php",{data: data, get_act_in: true, sub:onsubmit, token:token},function(rs){
      if(rs != undefined && rs.success){
        $("#accordion").html(rs.list);
        elastic.updBarChart(rs,grafica);
      }else{
        alert(rs.message);
      }
    });
    $("#container_loader_chart1").hide();
    this.query = {};
  },

  setAlerts: function(msg,tipo){
    // console.log("Alertas: ",msg,tipo);
    var tipo_alerta = tipo == 1 ? 'alert-danger alerts-danger-ppal-cc' : 'alert-success alerts-success-ppal-cc';
    var $_div_alert = '<div class="alert '+tipo_alerta+'">'+msg+'</div>';
    $("#alerts-ppal-cc").append($_div_alert);
    $(".alert").prop("hidden",false);
  },

  getMap: function(fecha,cc,mapa,onsubmit=0,token=''){
    var f = this.formatDate(fecha);
    this.query = {};
    this.setOrderSort('desc');
    this.setFilterRange(f);
    this.setQuery();
    this.setBool({"match":{"RuleName.keyword":""}});
    this.query["por_cc"] = cc;
    var list_alerts = "<ul>";
    $("#alerts-ppal-cc").empty();
    console.log("QUERY: ",JSON.stringify(this.query));
    $.post("./php/elasticsh.php",{data: this.query, get_map : true, sub:onsubmit, token:token}, function(rs){
      if(rs != undefined){
        if(rs.success){
          if(rs.data.length > 0){
            markerGroup.clearLayers();
            for(var i in rs.data){
              if(rs.data[i]['lat'] != null && rs.data[i]['lng']!= null){
                if(rs.data[i]['last'].length > 0){
                  var hoy = new Date();
                  var time_device = new Date(Date.parse(rs.data[i]['last'][1]));
                  var diff = (hoy.getTime() - time_device.getTime()) / (1000*60);
                  var color = diff < 30 ? '#139620' : '#f5ca32';
                }else var color = '#dd2020';
                if(color == '#dd2020') list_alerts += '<li>El cibercentro '+rs.data[i]['label']+' no ha tenido actividad</li>';
                var color_marker = setColor(color);
                var marker = L.marker([rs.data[i]['lat'],rs.data[i]['lng']],{icon: color_marker});
                marker.bindPopup(
                                 "<b><p>Cibercentro: "+rs.data[i]['label']+
                                 "</p><p>Tipo: "+rs.data[i]['tipo_sitio']+
                                 "</p><p>Total de dispositivos: "+rs.data[i]['devices']+
                                 "</p><p>Primer dispositivo conectado: "+(rs.data[i]['first'].length > 0 ? rs.data[i]['first'].join(' / ') : "Sin datos")+
                                 "</p><p>Ultimo dispositivo conectado: "+(rs.data[i]['last'].length > 0 ? rs.data[i]['last'].join(' / ') : "Sin datos")+
                                 "</p></b>"
                               );
                marker.addTo(markerGroup);
              }
            }
            list_alerts += "</ul>";
            // elastic.setAlerts(list_alerts,1);
            markerGroup.addTo(mapa);
            $("#container_loader_map").hide();
          }
        }
      }else{
        alert(rs.message);
      }
    });
    this.query = {};
  },

  aggs_alerts: {
    "ms-update": {
      "filter": {
        "term": {
          "Application.keyword": "ms-update"
        }
      }
    },
    "apt-get":{
      "filter": {
        "term": {
          "Application.keyword": "apt-get"
        }
      }
    }
  },

  getTotalAlerts: function(date){
    var fecha = this.formatDate(date);
    this.query = {};
    this.setFilterRange(fecha);
    this.setQuery();
    this.setBool();
    delete this.query.sort;
    delete this.query._source;
    this.query.size = 0;
    this.query['aggs'] = this.aggs_alerts;
    console.log("QUERY: ",JSON.stringify(this.query));
    $.post("./php/elasticsh.php",{data: this.query, get_total_alerts : true},function(rs){
      if(rs != undefined){
        var content = "<a class=\"iconmenu_list iconmenu_head\">alertas</a>";
        var hoy = new Date();
        var mes_tmp = parseInt(hoy.getMonth())+1;
        var mes = parseInt(mes_tmp) < 10 ? "0"+String(mes_tmp) : mes;
        var alertas = 0;
        for(var i in rs.alerts){
          alertas += parseInt(rs.alerts[i].doc_count);
          content += '<a class="iconmenu_list" href="./home.html?view='+(i == 'apt-get' ? '1' : '2')+'"><span class="iconmenu_alerts">'+rs.alerts[i].doc_count+'</span> <b class="blue">'+i+'</b><span class="iconmenu_date">'+(hoy.getFullYear()+"/"+mes+"/"+hoy.getDate())+'</span></a>';
        }
        $("#conteo_alerts_ppal").html(alertas);
        $("#div-alerts-ppal").html(content);
      }
    });
    this.query = {};
  },

  set_alerts_table: function(id,date,tabla,onsubmit=0,token=''){
    this.query = {};
    fecha = this.formatDate(date);
    this.setOrderSort('desc');
    this.setFilterRange(fecha);
    this.setQuery();
    this.setBool({
          "match": {
            "Application.keyword": id==1?"apt-get":"ms-update"
          }
        });
    console.log("QUERY: ",JSON.stringify(this.query));
    $.post("./php/elasticsh.php",{data: this.query, tabla_alerts:true, sub:onsubmit, token:token},function(rs){
      $("#container_loader_tabla_alert").show();
      if(rs != undefined){
        tabla.fnClearTable();
        for(var i in rs.data){
          tabla.fnAddData(rs.data[i]);
        }
        $("#container_loader_tabla_alert").hide();
      }
    });
    this.query = {};
  },

  download_logs: function(date,cc,token=''){
    date = this.formatDate(date);
    page = "./php/download.php?data="+btoa(date.join("|"))+"&cc="+cc+"&tkn="+token;
    window.location = page;
  }

};
