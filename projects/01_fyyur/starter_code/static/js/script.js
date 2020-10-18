window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

const deleteVenue = (venueId) => {
  fetch('/venues/' + venueId, {
    method: 'DELETE'
  })
  .then(response => {
    return response.json()
  })
  .then(jsonResponse => {
    if (jsonResponse['success'] == null) {
      alert('Error!')
    } else {
      location.replace("/")
    }
  })
  .catch(function(e) {
    alert('Error!')
  })
};

const deleteArtist = (venueId) => {
  fetch('/artists/' + venueId, {
    method: 'DELETE'
  })
  .then(response => response.json())
  .then(jsonResponse => {
    if(jsonResponse['success'] == null) {
      alert('Error!')
    } else {
      location.replace("/")
    }
  })
  .catch(function(e) {
    alert('Error!')
  })
};

jQuery(document).ready(function() {
  if ($("#seeking-talent")[0] && $("#seeking-talent")[0].checked) {
    $('#seeking-description-section').show();
  }

  $("#seeking-talent").change(function() {
      if (this.checked) {
          $('#seeking-description-section').show();
      } else {
          $('#seeking-description-section').hide();
      }
  });
});