<html>
<body>

<?php
$mysqli = new mysqli('mysql-d', 'd2465004rw', 'SQLGLcom','d2465004_devicesinlan');
if ($mysqli->connect_errno) {
    echo "Lo sentimos, no me he podido conectar a la base de datos.";
//    echo "Error no mostrable en producción: Fallo al conectarse a MySQL debido a: \n";
//    echo "Errno: " . $mysqli->connect_errno . "\n";
//    echo "Error: " . $mysqli->connect_error . "\n";
    exit;
}

echo "<h1>DevicesInLan installations</h1>";
echo "<ul>";

$cur=$mysqli->query("SELECT count(uuid) as count from installations");$row= $cur->fetch_row();
$totalinstallations=$row[0];
echo "<li>Total installations: " .$totalinstallations."</li>";

$cur=$mysqli->query("SELECT count(uuid) as count from installations where installation>=DATE(NOW()) - INTERVAL 30 DAY");$row= $cur->fetch_row();
echo "<li>Number of installations in the last 30 days: " .$row[0]."</li>\n";

$cur=$mysqli->query("SELECT count(uuid) as count from installations where lastuse>=DATE(NOW()) - INTERVAL 30 DAY");$row= $cur->fetch_row();
echo "<li>Number of installations used in the last 30 days: " .$row[0]."</li>\n";

$cur=$mysqli->query("SELECT lastversion, count(uuid) as count from installations group by lastversion order by lastversion desc");$row= $cur->fetch_row();
echo "<li>Installations in the last version (" . $row[0] . "): " . $row[1] . "</li>\n";
echo "</ul>";

echo "<h1>Platforms</h1>";
echo "<ul>";
$cur=$mysqli->query("SELECT count(uuid) as count from installations where platform='Linux'");$row= $cur->fetch_row();
$total=$row[0];
echo "<li>Linux installations: " .$total."</li>";
$cur=$mysqli->query("SELECT count(uuid) as count from installations where platform='Windows'");$row= $cur->fetch_row();
$total=$row[0];
echo "<li>Windows installations: " .$total."</li>";
echo "</ul>";


echo "<h1>Uses</h1>";
echo "<ul>";
$cur=$mysqli->query("SELECT sum(uses) as sum from installations");$row= $cur->fetch_row();
$total=$row[0];
echo "<li>Total uses: " .$total."</li>";
echo "</ul>";




$cur.close();
$mysqli->close();

?>

</body>
</html>

