<?php
// UNCOMMENT TO DEBUG
// ini_set('display_errors', 1);
// error_reporting(E_ALL);

function get_client_ip() {
    $ipaddress = '';
    if (isset($_SERVER['HTTP_X_REAL_IP']))
        $ipaddress = $_SERVER['HTTP_X_REAL_IP'];
    else if (isset($_SERVER['HTTP_TRUE_CLIENT_IP']))
        $ipaddress = $_SERVER['HTTP_TRUE_CLIENT_IP'];
    else
        $ipaddress = 'UNKNOWN';
    return $ipaddress;
}

if (isset($_GET['uuid'])==False) {
    echo "Some parameter is missing";
    exit;
}

if (isset($_GET['version'])==False) {
    echo "Some parameter is missing";
    exit;
}

if (isset($_GET['platform'])==False) {
    echo "Some parameter is missing";
    exit;
}

if (preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/', $_GET['uuid'])==False) {
    echo "It's not an uuid";
    exit;
}

$mysqli = new mysqli('mysql-d', 'd2465004rw', 'SQLGLcom','d2465004_devicesinlan');
if ($mysqli->connect_errno) {
    echo "Error: " . $mysqli->connect_error . "\n";
    exit;
}

$uuid=$mysqli->real_escape_string($_GET['uuid']);
$ip=$mysqli->real_escape_string(get_client_ip());
$version=$mysqli->real_escape_string($_GET['version']);
$platform=$mysqli->real_escape_string($_GET['platform']);

$sql = "SELECT uuid, uses from installations where uuid='$uuid'";
if (!$resultado = $mysqli->query($sql)) {
    echo "Error: " . $mysqli->error . "\n";
    exit;
}

if ($resultado->num_rows == 0){
    $sql = "INSERT INTO installations (uuid, installation, ip4, uses, lastversion, lastuse, platform) VALUES ('$uuid', now(), '$ip', 1, '$version', now(), '$platform')";
    if ($mysqli->query($sql)) {
        echo "Installation inserted";
    } else {
        echo "Installation not inserted";
        echo "Error: " . $mysqli->error . "\n";
    }
}
 else {
    $row=$resultado->fetch_row();
    $uses=$row[1]+1;
    $sql = "UPDATE installations set ip4='$ip', uses=$uses, lastversion='$version', lastuse=now(), platform='$platform' WHERE uuid='$uuid'";
    if ($mysqli->query($sql)) 
    {
        echo "Installation $uuid updated. Set $uses uses and $version version ";
    } else {
        echo "Installation not updated";
        echo "Error: " . $mysqli->error . "\n";
    }
}
$resultado->close();
$mysqli->close();

