<?php
    		$name=$_POST['name'];
    		$email=$_POST['email'];
    		$phone=$_POST['phone'];
    		$msg=$_POST['msg'];
    		$to='sculpturemyra@optonline.net'; // Receiver Email ID, Replace with your email ID
    		$subject='New Email from sculpturemyra.com visitor';
    		$message="Name :".$name."\n"."Phone :".$phone."\n"."Wrote the following :"."\n\n".$msg;
    		$headers="From: richalbreb@gmail.com.";
    		if(mail($to, $subject, $message, $headers)){
                header("Location: ../index.html");
    		}

?>
