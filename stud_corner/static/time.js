const round = (t, dsc) => `${Math.floor(t)} ${dsc} ago`;
function timedelta(el) {
  let date = el.getAttribute('time-delta');
  if (!date.includes('GMT')) {
    date = date + 'GMT';
  }
  let text = 'just now';
  let now = new Date();
  let datetime = new Date(date);
  let seconds = (now - datetime) / 1000; //in seconds
  if (seconds <= -1) {
    return;
  }
  let mins = seconds / 60;
  let hrs = mins / 60;
  let days = hrs / 24;
  let weeks = days / 7;
  if (weeks >= 4) {
    text = `${datetime.getDate()}`;
    let months = weeks / 4;
    let years = months / 12;
    if (months > 1 && months < 13) {
      text = round(months, 'months');
    } else {
      let dsc = 'year';
      if (years >= 2) {
        dsc = 'years';
      }
      text = round(years, dsc);
    }
  } else if (weeks >= 2) {
    text = round(weeks, 'weeks');
  } else if (days >= 2) {
    text = round(days, 'days');
  } else if (hrs >= 2) {
    text = round(hrs, 'hours');
  } else if (mins >= 2) {
    text = round(mins, 'minutes');
  }
  el.textContent = text;
}
let time_deltas = document.querySelectorAll('*[time-delta]');

const refresh_deltas = () =>time_deltas.forEach(timedelta);
refresh_deltas()
setInterval(refresh_deltas, 60000);
