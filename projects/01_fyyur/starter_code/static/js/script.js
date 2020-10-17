window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

const deleteVenue = (venueId) => {
  fetch('/venues/' + venueId, {
    method: 'DELETE'
  })
  .then(response => response.json())
  .then(jsonResponse => {
    if(jsonResponse['success'] == null) {
      console.log(jsonResponse)
      alert('Error!')
    } else {
      location.replace("/")
    }
  })
  .catch(function(e) {
    console.log(e)
    alert('Error!')
  })
};