//document: to control the html files
//addEventListener: to start listening for any event
//if Dom(Document Object Model) is loaded
//save it in anonymous function
document.addEventListener("DOMContentLoaded", function() {
    
    //Tab Persistence logic
    //let is used to dynamic variables in js
    let savedTab = localStorage.getItem('activeTab'); //to get the active tab
    if (savedTab) { //if it's exists
        let tabTrigger = document.querySelector(`#${savedTab}`); //save this tab in a dynamic variable
        if (tabTrigger) { //if it exists
            let tabInstance = new bootstrap.Tab(tabTrigger); //save the the tab trigger
            tabInstance.show(); //then shows the tab
        }
    }

    let tabElements = document.querySelectorAll('button[data-bs-toggle="pill"]'); //save all the buttons in a list
    tabElements.forEach(function(tabEl) { //loop inside this list
        tabEl.addEventListener('shown.bs.tab', function (event) { //to save the tab
            localStorage.setItem('activeTab', event.target.id); //saving the active tab into the local storage in the browser
        });
    });

    //Timer Logic
    function updateTimers() { //timer logic function
        let timers = document.querySelectorAll('.countdown-timer'); //selecting any elements with .countdown-timer class
        
        timers.forEach(function(timer) { //looping in timers
            let timeStr = timer.getAttribute('data-time'); //getting the attribute from the html files
            let targetDate = new Date(timeStr); //changing the time from str into date object
            let target = targetDate.getTime(); //saving the time from the start of the computers
            let type = timer.getAttribute('data-type'); //getting the attribute from the html files
            let now = new Date().getTime(); //get the time now
            let distance = target - now; //calculate the time
            
            let btnId = 'btn-' + timer.getAttribute('data-id'); //getting the trip id from the html file
            let btn = document.getElementById(btnId); //saving it
            
            //calaculating time
            let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)); //in hours
            let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)); //in minutes
            let seconds = Math.floor((distance % (1000 * 60)) / 1000); //in seconds
            
            //time display
            let timeDisplay = ""; //the default 
            if (hours > 0) { //if hours is more than 0
                timeDisplay = `${hours}h ${minutes}m ${seconds}s`; //display it in this formula H:M:S
            } else { //if it is less than
                timeDisplay = `${minutes}m ${seconds}s`;//display it in this formula H:M
            }

            
            
            
            if (type === 'departure') { //if the type is equal 'departure'
                if (distance < 0) { //if the timer countdown finished
                    timer.innerText = "Leaving Now!"; //change the timer text
                    timer.className = "countdown-timer timer-text text-danger"; //change the color into danger[red color]
                } else { //if the timer didn't reach 0
                    timer.innerText = `Leaving in: ${timeDisplay}`; //display the timer
                    timer.className = "countdown-timer timer-text text-hurry"; //change the color of the timer into hurry[orange color]
                    
                    if(btn && !btn.classList.contains('btn-danger')) { //if the button exsits and it's amrked as danger[red color]
                        btn.classList.remove('disabled', 'btn-secondary', 'pointer-none'); //remove all the limitations
                        btn.classList.add('btn-primary'); //add the new button color[blue color]
                        btn.innerText = "Book Now"; //change it to book now
                        btn.style.pointerEvents = "auto"; //change the state to auto to make the user have the ability to react with the button
                    }
                }
            } 
            else { //if the type is not equal 'departure'
                if (distance < 0) { //if the countdown is finished
                    timer.innerText = "Arriving Soon..."; //changing the timer text
                    timer.className = "countdown-timer timer-text text-wait"; //changing the timer color
                } 

                else if (distance <= 5 * 60 * 1000) { //if the countdown equal five minutes or below
                    timer.innerText = `Arrives in: ${timeDisplay}`; //display the timer
                    timer.className = "countdown-timer timer-text text-success"; //changing the color
                    
                    if(btn && !btn.classList.contains('btn-danger')) { //if the button exsits and it's amrked as danger[red color]
                        btn.classList.remove('disabled', 'btn-secondary', 'pointer-none'); //remove all the limitations
                        btn.classList.add('btn-primary'); //add the new button color[blue color]
                        btn.innerText = "Book Now"; //change it to book now
                        btn.style.pointerEvents = "auto"; //change the state to auto to make the user have the ability to react with the button
                    }
                } 

                else { //if the countdown timer is more than five minutes
                    timer.innerText = `Starts in: ${timeDisplay}`; //change the timer text
                    timer.className = "countdown-timer timer-text text-wait"; //changing the timer color
                    
                    if(btn && !btn.classList.contains('btn-danger')) { //if the button exsits and it's amrked as danger[red color]
                        btn.classList.add('disabled', 'btn-secondary', 'pointer-none'); //remove all the limitations
                        btn.innerText = "Wait"; //change the inner text into 'Wait'
                    }
                }
            }
        });
    }

    setInterval(updateTimers, 1000); //using the interval and countdown every second'1000 milli'
    updateTimers(); //using the function

    //Auto Refresh Logic
    if(document.querySelector('.auto-refresh')) { //if there is a class name with '.auto-refresh'
        setTimeout(() => location.reload(), 10000); //reload every 10 seconds
    }
});