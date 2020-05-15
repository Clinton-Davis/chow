/* Sending Emails Function */
function sendMail(contactForm) {
    emailjs
        .send("gmail", "chow", {
            from_name: contactForm.name.value,
            from_email: contactForm.emailaddress.value,
            message_request: contactForm.message.value
        })
        .then(
            function (responce) {
                if (responce.status == 200) {
                    location.href = "https://chow-flask-mongodb.herokuapp.com/";
                }
            },
            function (error) {
                console.log("FAILED", error);
            }
        );
    return false;
}