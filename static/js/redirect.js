function redirectToPage() {
    const select = document.getElementById("selectbox");
    const selectedOption = select.value;
    
    if (selectedOption === '') {
        window.location.href = "/";
    } else if (selectedOption === 'Home') {
        window.location.href = "/";
    } else if (selectedOption === 'Image') {
        window.location.href = "/image";
    } else if (selectedOption === 'Group Real Time Video') {
        window.location.href = "/group-real-time-video";
    } else if (selectedOption === 'Single Person Acting Practice') {
        window.location.href = "/single-person-acting-practice";
    } else if (selectedOption === 'Single Person Real Time Video') {
        window.location.href = "/single-person-real-time-video";
    } else if (selectedOption === 'Charts') {
        window.location.href = "/charts";
    }
}