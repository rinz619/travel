//  lightGallery(document.getElementById('lightgallery'));


document.querySelectorAll('[id^="lightgallery-"]').forEach(function(galleryEl) {
    lightGallery(galleryEl);
});