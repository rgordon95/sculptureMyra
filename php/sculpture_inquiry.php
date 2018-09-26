<?php
    		$name=$_POST['name'];
    		$email=$_POST['email'];
    		$phone=$_POST['phone'];
        $piece=$_POST['piece'];
        $price=$_POST['price'];
    		$msg=$_POST['msg'];
    		$to='sculpturemyra@optonline.net'; // Receiver Email ID, Replace with your email ID
    		$subject='New Email from sculpturemyra.com visitor';
    		$message="Name :".$name."\n"."Phone :".$phone."\n"."requested the following:"."\n\n".$piece."\n\n".$price."\n\n".$msg;
    		$headers="From: richalbreb@gmail.com.";
    		if(mail($to, $subject, $message, $headers)){
                header("Location: ../index.html");
    		}

?>
