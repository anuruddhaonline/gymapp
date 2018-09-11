

    $('#upbtn').click(function () {

        console.log('here');

        $nic = $('#nic').val();
        $bw = $('#weight').val();
        $bh = $('#height').val();
        $bc = $('#chest').val();
        $bf = $('#fat').val();

        console.log($nic);
        console.log($bw);
        console.log($bh);
        console.log($bc);
        console.log($bf);

      $.post("/savedetail" , {nic : $nic , weight :$bw ,height :$bh ,chest :$bc,fat :$bf} , function (data) {

        console.log(data);



     });

     getUserData();

     chart();


    });

    $(document).ready(function(){

        getUserData();
        chart();


    });


    function getUserData(){

    //$nic = "324324324V"

    $nic = $('#nic').val();

    console.log($nic);

     $.post("/getfilldetail" , {nic : $nic} , function (data) {


         $.each(data.out, function(index, value) {

         $('#mname').text(value.name+" "+value.lname);

        });


        console.log(data);

     });


    }







