//************************************************
// Name:         Michael Edukonis
// UIN:          677141300
// email:        meduk2@illinois.edu
// class:        CS437
// assignment:   Lab2
// date:         3/3/2023
//************************************************

var server_port = 65432;
var server_addr = "192.168.1.2";   // the IP address of your Raspberry PI
var timer;

//************************************************
//window is the global object for the web browser
//addEventListener function will execute on
//browser load and repeatedly run the update_stats
//function below
//************************************************
window.addEventListener("load", (event) => {
   timer = setInterval(update_stats, 5000);
});

//************************************************
//This is a delay function that will allow a
//another function to finish execetuing first
//this will be used in async functions below
//
//************************************************
function delay(time)
{
  return new Promise(resolve => setTimeout(resolve, time));
}

//************************************************
//Instance of tcp socket is created and retrieves
//picar stats date/time, battery level cpu temp,
//and cpu usage level.  Calculation is performed
//to get F anc C temp and web page elements address
//updated.  Data is received all at once as a JSON
//object which is then parsed for it's individual
//readings.  The entire JSON object can be seein
//in the browser's console output with new results
//every 5 seconds due to addeventlistner above.
//************************************************
function update_stats()
{

    const net = require('net');

    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        console.log('sending message to update stats');
        // send the message
        client.write("u");
        });


        // get the data from the server
    client.on('data', (data) => {
        //document.getElementById("greet_from_server").innerHTML = data;
        console.log(data.toString());
        pi_data = JSON.parse(data);
        //cpu_temp_conv = Math.round(((pi_data.cpu_temperature * 9 / 5 + 32)*10/10));
        cpu_temp_f = (pi_data.cpu_temperature * 9 / 5 + 32).toFixed(1)
        cpu_temp_c = pi_data.cpu_temperature.toFixed(1)
        document.getElementById("date").innerHTML = pi_data.date + " " + pi_data.time;
        document.getElementById("battery").innerHTML = pi_data.battery;
        document.getElementById("temperature").innerHTML = cpu_temp_f + "F " + "     " + cpu_temp_c + "C";
        document.getElementById("cpu").innerHTML = pi_data.cpu_usage +"%";

        client.end();
        client.destroy();
    });

}

//************************************************
//Instance of tcp socket is created and writes
//to the socket the command that coincides with
//car movement (see wifi_server.py on picar)
//also calls update_photo() function below
//************************************************
function drive(command)
{

    const net = require('net');

    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        console.log('sending message for movement');
        // send the message
        client.write(command);
    });
    update_photo()

}

//************************************************
//Instance of tcp socket is created and writes
//to the socket the command that coincides with
//taking a photo with the pi-cam.  This goes one
//way only and nothing comes back.  The photo is
//updated by the webserver running on the picar
//due to cache issues, whenever this function is
//called, must also call the change_photo_html_tag()
//function as well.
//************************************************
function update_photo()
{

    const net = require('net');

    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        console.log('sending message to update photo');
        // send the message
        client.write("p");
    });

    //reload the photo after it is captured from pi-cam
    change_photo_html_tag();

}

//************************************************
//Instance of tcp socket is created and writes
//to the socket the command that coincides with
//running an ultrasonic scan of the environment on
//the picar.  Data from that scan is plotted visually
//using matplotlib which generates a photo of the
//result on the webpage.  The photo is
//updated by the webserver running on the picar
//due to cache issues, whenever this function is
//called, must also call the change_scan_photo_html_tag()
//function as well.
//************************************************
function update_scan()
{

    const net = require('net');

    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        console.log('sending message to rescan environment');
        // send the message
        client.write('q');
    });

    change_scan_photo_html_tag();

}

//************************************************
//The picam on the car is running constantly however
//when instructed to capture a photo, it does not
//happen instantly.  It takes approximately 1 second
//from start to finish to successfully get a photo
//copy to the web browser folder and be ready for
//display.  Because the name never changes, cache
//issue will keep displaying an old version.  Adding
//the random number to the end but not actually in
//the tag text will force the browser to reload the
//image.  TODO: create new name on server side and
//send back new name over the socket.
//************************************************
async function change_photo_html_tag()
{
    var rand = Math.floor(Math.random() * 10000)
    //console.log('photo taken - reload new photo');
    var Image_Id = document.getElementById('pic');
    await delay(1000);
    Image_Id.src = "http://192.168.1.2/img.jpg?" +rand;   //+rand for cache busting

}

//************************************************
//It takes approximately 2 seconds to run the scan
//matplotlib to create the visual output,
//copy to the web browser folder and be ready for
//display.  Because the name never changes, cache
//issue will keep displaying an old version.  Adding
//the random number to the end but not actually in
//the tag text will force the browser to reload the
//image.  TODO: create new name on server side and
//send back new name over the socket.
//************************************************
async function change_scan_photo_html_tag()
{
    var rand = Math.floor(Math.random() * 10000)
    //console.log('photo taken - reload new photo');
    var Image_Id = document.getElementById('scan_pic');
    await delay(2000);
    Image_Id.src = "http://192.168.1.2/scan_result.jpg?" +rand;   //+rand for cache busting

}
