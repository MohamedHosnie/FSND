window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

$(".datetime-picker").Zebra_DatePicker({
  format: 'Y-m-d H:i:s',
  direction: 1
});
  