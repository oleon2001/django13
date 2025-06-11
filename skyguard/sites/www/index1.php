<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<title>Logitrack</title>
<link href="estilo2.css" rel="stylesheet" type="text/css" media="all" />
<link href='http://fonts.googleapis.com/css?family=Quattrocento+Sans' rel='stylesheet' type='text/css'>
<script type="text/javascript" src="jquery-1.2.6.min.js"></script>
<link rel="stylesheet" href="http://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css" />
  <script src="http://code.jquery.com/jquery-1.9.1.js"></script>
  <script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
  <link rel="stylesheet" href="/resources/demos/style.css" />
  <script>
  $(function() {
    $( "#dialog" ).dialog({
      autoOpen: false,
      show: {
        effect: "blind",
        duration: 1000
      },
      hide: {
        effect: "explode",
        duration: 1000
      }
    });
 
    $( "#opener" ).click(function() {
      $( "#dialog" ).dialog( "open" );
    });
  });
  </script>

<style type="text/css">
#slideshow {
    position:relative;
    height:220px; margin-left:0px;
}

#slideshow IMG {
    position:absolute;
    top:0;
    left:0;
    z-index:8;
    opacity:0.0;
}

#slideshow IMG.active {
    z-index:10;
    opacity:1.0;
}

#slideshow IMG.last-active {
    z-index:9;
}
.registro { font-size:12px;}
</style>

<script type="text/javascript">
function slideSwitch() {
    var $active = $('#slideshow IMG.active');

    if ( $active.length == 0 ) $active = $('#slideshow IMG:last');

    // use this to pull the images in the order they appear in the markup
    var $next =  $active.next().length ? $active.next()
        : $('#slideshow IMG:first');

    // uncomment the 3 lines below to pull the images in random order
    
    // var $sibs  = $active.siblings();
    // var rndNum = Math.floor(Math.random() * $sibs.length );
    // var $next  = $( $sibs[ rndNum ] );


    $active.addClass('last-active');

    $next.css({opacity: 0.0})
        .addClass('active')
        .animate({opacity: 1.0}, 1000, function() {
            $active.removeClass('active last-active');
        });
}

$(function() {
    setInterval( "slideSwitch()", 7000 );
});


</script>
<link rel="shortcut icon" href="favicon.ico" type="image/x-icon" />

</head>

<body>
<div id="cont_home">
<div id="header_top">
  <table width="1200" height="107" border="0">
    <tr>
      <td width="711" rowspan="2"><a href="index.php"><img src="logo.jpg" width="680" height="74" alt="Logitrack" /></a></td>
      <td height="38" colspan="4">&nbsp;</td>
    </tr>
    <tr>
      <td width="122" align="center" valign="bottom"><a href="soluciones.html">Soluciones </a></td>
      <td width="122" align="center" valign="bottom"><a href="energeticos.html">Energéticos</a></td>
      <td width="122" align="center" valign="bottom"><a href="empresa.html">Empresa</a></td>
      <td width="122" align="center" valign="bottom"><a href="contacto.html">Contacto</a></td>
    </tr>
  </table>
</div>

<div id="header">
  <div id="login">
    <form id="form1" name="form1" method="post" action="">
      <table width="188" height="166" border="0">
        <tr>
          <td width="20" height="14">&nbsp;</td>
          <td width="65">&nbsp;</td>
          <td width="58">&nbsp;</td>
          <td width="27">&nbsp;</td>
        </tr>
        <tr>
          <td height="19">&nbsp;</td>
          <td colspan="2">ACCESO A CLIENTES</td>
          <td>&nbsp;</td>
        </tr>
        <tr>
          <td height="45">&nbsp;</td>
          <td colspan="2"><label for="usuario">Usuario</label>
          <input type="text" name="usuario" id="usuario" /></td>
          <td>&nbsp;</td>
        </tr>
        <tr>
          <td height="52">&nbsp;</td>
          <td colspan="2"><label for="password">Contraseña</label>
          <input type="text" name="password" id="password" /></td>
          <td>&nbsp;</td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td><input type="submit" name="entrar" id="entrar" value="Entrar" /></td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
        </tr>
        </table>
    </form>
    
    <table width="150" border="0">
  <tr>
    <td width="18">&nbsp;</td>
    <td width="122" align="center"><div id="dialog" title="Formulario de Registro">
 <h5> <span class="registro">Los campos con (*) son requeridos </span></h5>
 <p>&nbsp;</p>
		<form method="POST" action="">
			<table>
				<tr>
					<td class="registro">Nombre y apellidos: </td>
				  </tr>
				<tr>
					<td class="registro">
					  <input type="name" name="nombre" />
					</td>
				  </tr>
				<tr>
					<td class="registro">*Usuario</td>
				  </tr>
				<tr>
				  <td>				    <span class="registro">
				    <input type="name" name="user" />				  
				    </span></td>
				  </tr>
				<tr>
				  <td class="registro">*Contraseña: </td>
				  </tr>
				<tr>
				  <td>				    <span class="registro">
				    <input type="password" name="pasword" />				  
				    </span></td>
				  </tr>
				<tr>
				  <td class="registro">*Repetir contraseña: </td>
				  </tr>
				<tr>
				  <td>				    <span class="registro">
				    <input type="password" name="rpasword" />				  
				    </span></td>
				  </tr>
			</table>
			<p class="registro">&nbsp;			  </p>
			<p class="registro">
			  <input type="submit" name="submit" value="Registrar" /> 
			  <input type="reset" />
			  </p>
        </form>
		<p>
		  <?php
			if (isset($_POST['submit'])) {
				require("enviar.php");
			}
		?>
		  </p>
		<p>&nbsp;</p>
    </div>
<p>&nbsp;</p> 
</td>
  </tr>
</table>
  </div>
  <div id="banner">
  <div id="slideshow">
    <img src="banner1.jpg" alt="Slideshow Image 1" class="active" />
    <img src="banner2.jpg" alt="Slideshow Image 2" />
	<img src="banner3.jpg" alt="Slideshow Image 2" />
</div>
 </div>
</div>
<div id="smart"><a href="soluciones.html">
  <div id="smart_in">
    <table width="1200" border="0">
      <tr>
        <td width="573" rowspan="3">&nbsp;</td>
        <td width="38" rowspan="3">&nbsp;</td>
        <td width="305" height="25">&nbsp;</td>
        <td width="266">&nbsp;</td>
      </tr>
      <tr>
        <td height="81" align="left" valign="top"><p>Sistema integral de pesaje que monitorea la carga en tiempo real por medio de satélite y GPS</p>
          <p>&nbsp;</p>
        <p><a href="soluciones.html">+ Ver más</a></p></td>
        <td>&nbsp;</td>
      </tr>
      <tr>
        <td height="150">&nbsp;</td>
        <td>&nbsp;</td>
      </tr>
    </table>
  </div></a> 
</div>

  <div id="text1_in">
    <table width="1200" border="0" align="center">
      <tr>
        <td width="82" height="42">&nbsp;</td>
        <td width="412">&nbsp;</td>
        <td width="107">&nbsp;</td>
        <td width="442">&nbsp;</td>
        <td width="135">&nbsp;</td>
      </tr>
      <tr>
        <td height="49">&nbsp;</td>
        <td><img src="t_tecnologias.jpg" alt="Tecnología a su servicio" width="229" height="23" /></td>
        <td>&nbsp;</td>
        <td><img src="t_soporte.jpg" alt="Soporte profesional" width="195" height="25" /></td>
        <td>&nbsp;</td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td valign="top"><p>El software de Logitrack proporciona  a nuestros clientes el poder de monitorear el peso de la carga y sus equipos en  tiempo real desde la comodidad de su oficina u hogar, logrando su absoluta  tranquilidad.</p></td>
        <td valign="top">&nbsp;</td>
        <td valign="top"><p>Desarrollamos nuestros propios productos con la más avanzada tecnología y estándares de calidad internacional. Nuestro equipo de trabajo está altamente capacitado en implementación, mantenimiento, innovación, y servicio de sistemas de seguridad.</p></td>
        <td>&nbsp;</td>
      </tr>
    </table>
  </div>

  <div id="text1_in">
    <table width="1200" border="0" align="center">
      <tr>
        <td width="82" height="42">&nbsp;</td>
        <td width="412">&nbsp;</td>
        <td width="107">&nbsp;</td>
        <td width="442">&nbsp;</td>
        <td width="135">&nbsp;</td>
      </tr>
      <tr>
        <td height="49">&nbsp;</td>
        <td><img src="t_impulso.jpg" alt="Impulso" width="278" height="24" /></td>
        <td>&nbsp;</td>
        <td><img src="t_soluciones.jpg" alt="Soluciones" width="254" height="24" /></td>
        <td>&nbsp;</td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td valign="top">Nuestros sistemas brindan ahorros significativos, evitando robos, gastos innecesarios y pérdidas de tiempo. De esta manera las empresas pueden canalizar sus recursos de una mejor forma.</td>
        <td valign="top">&nbsp;</td>
        <td valign="top"><p>Proponemos soluciones a la medida por medio de avances tecnológicos y  una gamma de servicios innovadores para proteger su carga, vehículos y  conductores.</p></td>
        <td>&nbsp;</td>
      </tr>
    </table>
  </div>

  <div id="menu_in">
    <div id="menu_der">
      <table width="800" border="0">
        <tr>
          <td width="77" height="34">&nbsp;</td>
          <td width="146" valign="bottom"> <strong>Mapa del Sitio</strong></td>
          <td width="82" valign="bottom"><a href="index.php">Inicio</a></td>
          <td width="114" valign="bottom"><a href="soluciones.html">Soluciones</a></td>
          <td width="114" valign="bottom"><a href="energeticos.html">Energéticos</a></td>
          <td width="114" valign="bottom"><a href="empresa.html">Empresa</a></td>
          <td width="123" valign="bottom"><a href="contacto.html">Contacto</a></td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td class="submenu"><a href="soluciones.html">Carga</a></td>
          <td>&nbsp;</td>
          <td class="submenu"><a href="empresa.html">Nosotros</a></td>
          <td>&nbsp;</td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td class="submenu"><a href="llantas.html">Llantas</a></td>
          <td>&nbsp;</td>
          <td class="submenu"><a href="empresa.html">Ventas</a></td>
          <td>&nbsp;</td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td class="submenu"><a href="combustibles.html">Combustible</a></td>
          <td>&nbsp;</td>
          <td class="submenu"><a href="empresa.html">Distribuidores</a></td>
          <td>&nbsp;</td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td class="submenu"><a href="conductor.html">Conductor</a></td>
          <td>&nbsp;</td>
          <td class="submenu">&nbsp;</td>
          <td>&nbsp;</td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td class="submenu"><a href="localizacion.html">Localización</a></td>
          <td>&nbsp;</td>
          <td class="submenu">&nbsp;</td>
          <td>&nbsp;</td>
        </tr>
      </table>
      <table width="790" height="53" border="0">
        <tr>
          <td colspan="2" align="right" valign="middle"><img src="sep_2.jpg" width="730" height="11" /></td>
        </tr>
        <tr>
          <td width="80">&nbsp;</td>
          <td width="738">Copyright © 2013 LOGITRACK ® . Todos los derechos reservados.</td>
        </tr>
      </table>
    </div><div id="menu_izq">
      <table width="400" border="0">
        <tr>
          <td width="59" rowspan="2"><img src="sep_1.jpg" width="10" height="154" /></td>
          <td height="58" colspan="2"><p><img src="logo_logitrackAZUL.jpg" width="220" height="46" alt="Logitrack" /></p>
          </td>
        </tr>
        <tr>
          <td width="465"><p class="submenu">Domingo M. Treviño #125 - 2B</p>
            <p class="submenu">Col. Santa María<br />
              Monterrey, MÉXICO<br />
            T. (81) 8303 2831 | (81) 8335 0211</p>
            <p class="submenu">&nbsp;</p>
          <p class="submenu"><a href="mailto:info@logitrack.com.mx">info@logitrack.mx</a></p>
          </td>
          <td width="262">&nbsp;</td>
        </tr>
      </table>
    </div>
  </div>
</div>
</body>
</html>