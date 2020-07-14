var iOS = !!navigator.platform && /iPad|iPhone|iPod/.test(navigator.platform);
var Android = !!navigator.platform && /Android|Linux|Linux armv6l|Linux armv7l/.test(navigator.platform);

if (iOS || Android) {
  window.location = __didcomm_url;
}
