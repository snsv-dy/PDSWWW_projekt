
window.addEventListener('load', function () {
	var time_div = document.getElementById('time_div');
	if(time_div.textContent == ''){
		time_div.textContent = '1624129200000';
	}

	var countDownDate = parseInt(time_div.textContent);

	// Update the count down every 1 second
	updateTime(countDownDate, null);
	var x = setInterval(updateTime, 1000, countDownDate, x);
});

function updateTime(countDownDate, thisInterval) {
	console.log('working');
  // Get today's date and time
  var now = new Date().getTime();

  // Find the distance between now and the count down date
  var distance = countDownDate - now;

  // Time calculations for days, hours, minutes and seconds
  var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);

  // Display the result in the element with id="demo"
  time_div.textContent = 'Pozostały czas: ' + hours + "h "
  + minutes + "m " + seconds + "s ";

  // If the count down is finished, write some text
  if (distance < 0) {
	clearInterval(thisInterval);
	time_div.textContent = "Koniec czasu";
  }
}
