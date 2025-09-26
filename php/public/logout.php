<?php
session_start();
// Clear session and redirect to logged out page
session_unset();
session_destroy();
header('Location: /loggedout.php');
exit;
