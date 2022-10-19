window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};


// const dateTimePicker = document.querySelector("#datetimepicker");
// dateTimePicker.datetimepicker();

// $(function () {
//   $('#datetimepicker1').datetimepicker();
// });

const deleteVenue = document.getElementById("delete-venue");

deleteVenue.onclick = function(e) {
    e.preventDefault();
    console.log('Delete event: ',e);
    const venueId = e.target.dataset['id'];
    fetch ('/venues/' + venueId, {
        method: 'DELETE'
    }).then(function(response) {
      // console.log("Deleted object")
      // window.location.replace(response.json()['redirect_url']);
      return response.json();
    }).then(function(responseJSON){
      if(responseJSON['status'] == 'success'){
				window.location.href = '/'
			} else {
				alert(responseJSON['statusMessage']);
			}
    })
};


const deleteBtn = document.getElementById("delete_venue");
  deleteBtn.addEventListener('click', (e) => {
		const venueId = e.target.dataset["id"];
		fetch('/venues/' + venueId , {
			method: 'DELETE'
		})
		.then(response => response.json())
		.then(jsonResponse => {
			if(jsonResponse['status'] === 'success'){
				window.location.href = '/'
			} else {
				alert(jsonResponse['message']);
			}
		})
	});



// deleteBtn.onclick = function(e) {
//   console.log("Delete event: ", e);
//   const listId = e.target.dataset.id;

//   fetch('/lists/'+ listId + '/delete',{
//   method: 'DELETE'
//   }).then(function() {
//   console.log('Parent?', e.target);
//   const item = e.target.parentElement;
//   item.remove();
//       document.getElementById("error").className = "hidden";
//       window.location.reload(true);
//   })
//   .catch(function(e) {
//       console.error(e);
//       document.getElementById("error").className = "";
//   });
// };

