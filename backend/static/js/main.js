
    // For sidebar
    const sidebar = document.getElementById("mySidebar");
    const sidebarToggle = document.querySelector(".nav-icon1");

    document.addEventListener('click', function(event) {
        if (!sidebar.contains(event.target) && event.target !== sidebarToggle) {
            closeNav();
        }
    });

    function openNav() {
        sidebar.style.right = "0";
    }

    function closeNav() {
        sidebar.style.right = "-1500px";
    }

    // For the second sidebar
    const topbar = document.getElementById("responsivetopbar");
    const topbarToggle = document.querySelector(".nav-icon2");
    
    topbarToggle.addEventListener('click', function(event) {
        toggleTopbar();
    });
    
    function toggleTopbar() {
        if (window.innerWidth <= 650) {
            if (topbar.style.height === "235px") {
                closeTopbar();
            } else {
                openTopbar();
            }
        } else {
            if (topbar.style.height === "220px") {
                closeTopbar();
            } else {
                openTopbar();
            }
        }
    }
    
    function openTopbar() {
        if (window.innerWidth <= 650) {
            topbar.style.height = "235px";
        } else {
            topbar.style.height = "220px";
        }
    }
    
    function closeTopbar() {
        topbar.style.height = "0";
    }
    
    // Scroll nav
    window.addEventListener('scroll', function() {
        var navWrapper = document.getElementById('navWrapper');
        if (window.scrollY > 100) {
            navWrapper.classList.add('fixed');
            navWrapper.style.opacity = "1";
        } else {
            navWrapper.classList.remove('fixed');
            navWrapper.style.opacity = "1";
        }
    });