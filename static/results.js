console.log("test");
// $(window).on("load", function() {  
//     console.log("test");     
//     while (true){
//         console.log("test");
//         $.ajax({
//                 type: "GET",
//                 url: "/get_result",
//                 success: function(response){
//                     console.log(response);
//                 }
//             })
//     }
// });

$.ajax({
    type: "GET",
    url: "/get_result",
    success: function(response){
        console.log(response);
    }
})