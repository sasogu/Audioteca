---
layout: default
title: "Lista de correo"
permalink: /lista-correo/
---

<section class="post">
  <header class="section-heading">
    <p class="post-meta">Contacto</p>
    <h1 class="post-title">Lista de correo</h1>
  </header>

  <div class="post-content">
    <style type="text/css">
      form#WebToLeadForm,
      form#WebToLeadForm * {
        margin: 0;
        padding: 0;
        border: none;
        color: #333;
        font-size: 12px;
        line-height: 1.6em;
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
      }
      form#WebToLeadForm {
        float: left;
        border: 1px solid #ccc;
        margin: 10px;
      }
      form#WebToLeadForm h1 {
        font-size: 32px;
        font-weight: bold;
        background-color: rgb(60, 141, 188);
        color: rgb(247, 247, 247);
        padding: 10px 20px;
      }
      form#WebToLeadForm h2 {
        font-size: 24px;
        font-weight: bold;
        background-color: rgb(60, 141, 188);
        color: rgb(247, 247, 247);
        padding: 10px 20px;
      }
      form#WebToLeadForm h3 {
        font-size: 12px;
        font-weight: bold;
        padding: 10px 20px;
      }
      form#WebToLeadForm h4 {
        font-size: 10px;
        font-weight: bold;
        padding: 10px 20px;
      }
      form#WebToLeadForm h5 {
        font-size: 8px;
        font-weight: bold;
        padding: 10px 20px;
      }
      form#WebToLeadForm h6 {
        font-size: 6px;
        font-weight: bold;
        padding: 10px 20px;
      }
      form#WebToLeadForm p {
        padding: 10px 20px;
      }
      form#WebToLeadForm input,
      form#WebToLeadForm select,
      form#WebToLeadForm textarea {
        border: 1px solid #ccc;
        display: block;
        float: left;
        min-width: 170px;
        padding: 5px;
      }
      form#WebToLeadForm select {
        background-color: white;
      }
      form#WebToLeadForm input[type="button"],
      form#WebToLeadForm input[type="submit"] {
        display: inline;
        float: none;
        padding: 5px 10px;
        width: auto;
        min-width: auto;
      }
      form#WebToLeadForm input[type="checkbox"],
      form#WebToLeadForm input[type="radio"] {
        width: 18px;
        min-width: auto;
      }
      form#WebToLeadForm div.col {
        display: block;
        float: left;
        width: 330px;
        padding: 10px 20px;
      }
      form#WebToLeadForm div.clear {
        display: block;
        float: none;
        clear: both;
        height: 0px;
        overflow: hidden;
      }
      form#WebToLeadForm div.center {
        text-align: center;
      }
      form#WebToLeadForm div.buttons {
        padding: 10px 0;
        border-top: 1px solid #ccc;
        background-color: #f7f7f7;
      }
      form#WebToLeadForm label {
        display: block;
        float: left;
        width: 160px;
        font-weight: bold;
      }
      form#WebToLeadForm span.required {
        color: #ff0000;
      }
    </style>

    <form id="WebToLeadForm" action="https://caminomedio.sinergiacrm.org/index.php?entryPoint=WebToPersonCapture" method="POST" name="WebToLeadForm">
      <h2></h2>
      <p>Esta lista de correo es un espacio sencillo para compartir reflexiones, entradas de blog y episodios del podcast que voy publicando como parte de mi práctica y enseñanza del budismo Soto Zen. Los envíos son ocasionales y puedes darte de baja cuando lo desees.</p>
      <div class="row">
        <div class="col"><label>Nombre: </label><input name="first_name" id="first_name" type="text" /></div>
        <div class="col">&nbsp;</div>
        <div class="clear">&nbsp;</div>
      </div>
      <div class="row">
        <div class="col"><label>Apellidos: <span class="required">*</span></label><input name="last_name" id="last_name" type="text" required="" /></div>
        <div class="col">&nbsp;</div>
        <div class="clear">&nbsp;</div>
      </div>
      <div class="row">
        <div class="col"><label>Correo electrónico: </label><input name="email1" id="email1" type="email" /></div>
        <div class="col">&nbsp;</div>
        <div class="clear">&nbsp;</div>
      </div>
      <div class="row center buttons">
        <input class="button" name="Submit" type="submit" value="Enviar" onclick="submit_form();" />
        <div class="clear">&nbsp;</div>
      </div>
      <input name="campaign_id" id="campaign_id" type="hidden" value="00000707-e538-14d1-d6d7-6975ddfb7dd1" />
      <input name="redirect_url" id="redirect_url" type="hidden" value="https://www.daizansoriano.com" />
      <input name="assigned_user_id" id="assigned_user_id" type="hidden" value="00000f0b-aea0-cbf0-db07-682dc6e0639d" />
      <input name="moduleDir" id="moduleDir" type="hidden" value="Leads" />
    </form>

    <div class="notranslate" style="all: initial;">&nbsp;</div>

    <script type="text/javascript">
      // STIC-custom 20211122 - jch - Avoid multiple submission
      // STIC#489
      var formHasAlreadyBeenSent = false;
      /**
       * Prevent multiple form submissions
       *
       * @return void
       */
      function lockMultipleSubmissions() {
        if (formHasAlreadyBeenSent) {
          console.log("Form is locked because it has already been sent.");
          event.preventDefault();
        }
        formHasAlreadyBeenSent = true;
      }
      // Attach function to event
      document.getElementById("WebToLeadForm").addEventListener("submit", lockMultipleSubmissions);
      // END STIC-custom
      function submit_form() {
        check_webtolead_fields();
        //document.WebToLeadForm.submit();
      }

      function check_webtolead_fields() {
        if (document.getElementById("bool_id") != null) {
          var reqs = document.getElementById("bool_id").value;
          bools = reqs.substring(0, reqs.lastIndexOf(";"));
          var bool_fields = new Array();
          var bool_fields = bools.split(";");
          nbr_fields = bool_fields.length;
          for (var i = 0; i < nbr_fields; i++) {
            if (document.getElementById(bool_fields[i]).value == "on") {
              document.getElementById(bool_fields[i]).value = 1;
            } else {
              document.getElementById(bool_fields[i]).value = 0;
            }
          }
        }
      }
    </script>
  </div>
</section>
