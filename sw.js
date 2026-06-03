self.addEventListener('install', (e) => {
  console.log('Service Worker: Installed');
});

self.addEventListener('fetch', (e) => {
  // PWA ইনস্টলের শর্ত পূরণ করার জন্য এই ইভেন্টটি রাখা হলো। 
  // এটি আপনার ওয়েবসাইটের অন্যান্য কোনো কাজে বাধা দেবে না।
});
