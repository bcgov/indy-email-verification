var iOS = !!navigator.platform && /iPad|iPhone|iPod/.test(navigator.platform);

if (iOS) {
  window.location = __streetcred_url;
}
