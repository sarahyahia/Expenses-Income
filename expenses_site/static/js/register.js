const usernameField = document.querySelector('#usernameField');
const emailField = document.querySelector('#emailField');
const passwordField = document.querySelector('#passwordField');
const userFeedbackField = document.querySelector('.invalid_feedback');
const emailFeedbackField = document.querySelector('.email_invalid_feedback');
const usernameSuccessOutput = document.querySelector(".usernameSuccessOutput");
const emailSuccessOutput = document.querySelector(".emailSuccessOutput");
const submitBtn = document.querySelector(".submit-btn")
const showPassword = document.querySelector("#showPasswordField");



const handleShowPassword =() =>{
    (showPassword.checked)
    ?passwordField.setAttribute("type","text")
        :passwordField.setAttribute("type","password")
    
}

showPassword.onclick = handleShowPassword;

usernameField.addEventListener('keyup',(e)=>{
    const usernameValue = e.target.value;
    usernameField.classList.remove("is-valid");
    usernameField.classList.remove("is-invalid");
    userFeedbackField.style.display = 'none';
    
    if (usernameValue.length>0){
        usernameSuccessOutput.style.display = 'block';
        usernameSuccessOutput.textContent = `checking ${usernameValue}`;

        fetch("/auth/validate-username", {
            body: JSON.stringify({ username: usernameValue }),
            method: "POST",
            headers : { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        }).then((response) => response.json())
        .then((data) => {
            usernameSuccessOutput.style.display = 'none';

            if(data.username_error){
                usernameField.classList.add("is-invalid");
                userFeedbackField.style.display = 'block';
                userFeedbackField.innerHTML = `<p class="mx-3">${data.username_error}</p>`;
                submitBtn.disabled = true;
            } else {
                usernameField.classList.add("is-valid");
                submitBtn.removeAttribute("disabled");
            }
        }).catch(error => {console.error(error);});
    }else{
        usernameSuccessOutput.style.display = 'none';
    }
})

emailField.addEventListener('keyup',(e)=>{
    let emailValue = e.target.value;
    emailField.classList.remove("is-invalid");
    emailField.classList.remove("is-valid");
    emailFeedbackField.style.display = 'none';
    
    if (emailValue.length>0){
        emailSuccessOutput.style.display = 'block';
        emailSuccessOutput.textContent = `checking ${emailValue}`;

        fetch("/auth/validate-email", {
            body: JSON.stringify({ email: emailValue }),
            method: "POST",
            headers : { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        }).then((response) => response.json())
        .then((data) => {
            emailSuccessOutput.style.display = 'none';

            if(data.email_error){
                emailField.classList.add("is-invalid");
                emailFeedbackField.style.display = 'block';
                emailFeedbackField.innerHTML = `<p class="mx-3">${data.email_error}</p>`;
                submitBtn.disabled = true;
            } else {
                emailField.classList.add("is-valid");
                submitBtn.removeAttribute("disabled");
            }
        })
    }else{
        emailSuccessOutput.style.display = 'none';
    }
})