require("nativescript-localstorage");
var SHA256 = require("nativescript-toolbox/crypto-js/sha256");
var fs=require("file-system");
var dialogs = require("tns-core-modules/ui/dialogs");
var LoadingIndicator = require("nativescript-loading-indicator").LoadingIndicator;
var Http = require("http");
var frameModule = require("ui/frame");
var webViewModule = require("ui/web-view");
var webView = new webViewModule.WebView();
var loader = new LoadingIndicator();
var page;




exports.loaded = function(args) {
    /*
    This gets a reference this page’s <Page> UI component. You can
    view the API reference of the Page to see what’s available at
    https://docs.nativescript.org/api-reference/classes/_ui_page_.page.html
    */
    page = args.object;
    // console.log(SHA256("Message"));

    /*
    A page’s bindingContext is an object that should be used to perform
    data binding between XML markup and JavaScript code. Properties
    on the bindingContext can be accessed using the {{ }} syntax in XML.
    In this example, the {{ message }} and {{ onTap }} bindings are resolved
    against the object returned by createViewModel().

    You can learn more about data binding in NativeScript at
    https://docs.nativescript.org/core-concepts/data-binding.
    */

}

exports.signUpPage = function() {

    page.closeModal();
    var loadSignUp = {
        moduleName: 'pages/signup/signup'
    }

    frameModule.topmost().navigate(loadSignUp);

}

function validate(type, val) {

    var username_regex = /^(\S+)([A-z]+)([0-9]*)([-_]*)$/g;
    var password_regex = /^(\S+)$/;
    var email_regex = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    var pass = /([a-z]+)/;
    var pass_1 = /([0-9]+)/;
    var pass_2 = /([!_-]+)/;
    var pass_3 = /([A-Z]+)/; //end of regex for password

    if (type == "username") {

        if (username_regex.test(val) && val.length > 2) {

            console.log("username");
            console.log(val);
            return true;

        } else {

            console.log("Error in username");
            return false;

        }


    } else if (type == "password") {

        if (password_regex.test(val) && val.length == 6) {

            console.log("password");
            console.log(val);
            return true;

        } else {

            console.log("Error in password");
            return false;

        }


    } else if (type == "email") {

        if (email_regex.test(val) && val.length > 2) {

            console.log("email");
            console.log(val);
            return true;

        } else {

            console.log("Error in email");
            return false;

        }


    }


}

var username;
var password;

exports.refill = function() {

    username = page.getViewById("user_email");
    password = page.getViewById("user_pass");
    var btn_sub = page.getViewById("btn_sub");
    var btn_login = page.getViewById("btn_login");
    var info_c = page.getViewById("info_c");
    var info_h = page.getViewById("info_h");
    var info_d = page.getViewById("none");
    var resend = page.getViewById("resend");
    var refill = page.getViewById("refill");
    var signup = page.getViewById("signup");

    info_c.visibility = "collapsed";
    info_h.visibility = "visible";
    password.visibility = "collapsed";
    username.visibility = "visible";
    info_d.visibility = "visible";
    btn_login.visibility = "visible";
    btn_sub.visibility = "collapsed";
    signup.visibility = "visible";
    refill.visibility = "collapsed";
    resend.visibility = "collapsed";

}


exports.loginAcct = function() {


    // var password_val = password.text;
    indicator = page.getViewById("indicator");
    username = page.getViewById("user_email");
    password = page.getViewById("user_pass");
    var btn_sub = page.getViewById("btn_sub");
    var btn_login = page.getViewById("btn_login");
    var info_c = page.getViewById("info_c");
    var info_h = page.getViewById("info_h");
    var info_d = page.getViewById("none");
    var resend = page.getViewById("resend");
    var refill = page.getViewById("refill");
    var signup = page.getViewById("signup");


    var username_val = username.text;

    if (validate("username", username_val) != true && validate("email", username_val) != true) {

        var options = {
            title: "Form Error",
            message: "Invalid username or email",
            okButtonText: "OK"
        };
        dialogs.alert(options).then(() => {
            console.log("username is invalid!");
        });

    } else {

        // var options = {
        //     title: "Form Sucess",
        //     message: "Valid",
        //     okButtonText: "OK"
        // };
        // dialogs.alert(options).then(() => {
        //     console.log("username is valids!");
        // });
        // indicator.busy = "true";
        // indicator.visibility = "visible";
        loader.show();
        token =SHA256(Math.random());
        console.log(token);
        
        Http.request({
            url: 'https://api.intelijence.com/paymiumm/generatePasswordToken',
            method: "POST",
            headers: { "Content-Type": "application/json" },
            content: JSON.stringify({ "usr": username_val, "t__Ukn__r_z_A_R": (token.toString()) })
        }).then(function(res) {
            // indicator.busy = "false";
            // indicator.visibility = "collapsed";
            loader.hide();
            var res = res.content.toJSON();

            console.log("ddd: "+res['res']);

            if (res['res'] == "success") {

                info_c.visibility = "visible";
                info_h.visibility = "collapsed";
                password.visibility = "visible";
                username.visibility = "collapsed";
                info_d.visibility = "collapsed";
                btn_login.visibility = "collapsed";
                btn_sub.visibility = "visible";
                signup.visibility = "collapsed";
                refill.visibility = "visible";
                resend.visibility = "visible";
                generateToken(token);
                validateToken(token.toString())

            } else if (res['res'] == "error") {




                var options = {
                    title: "Form Error",
                    message: "Sorry an error occured, resend form",
                    okButtonText: "OK"
                };

                dialogs.alert(options).then(function() {

                });




            } else if (res['res'] == "unconfirmed") {


                var options = {
                    title: "Form Error",
                    message: "Please confirm your email, to access this account",
                    okButtonText: "OK"
                };

                dialogs.alert(options);

            } else if (res['res'] == "pswdErr") {




                var options = {
                    title: "Form Error",
                    message: "An OTP has already been sent you, please refer to the previously requested sent OTP",
                    okButtonText: "OK"
                };

                dialogs.alert(options).then(function() {

                });




            } else {

                var options = {
                    title: "Form Error",
                    message: "Invalid account detail",
                    okButtonText: "OK"
                };

                dialogs.alert(options);

            }


        }, function(error) {


            // indicator.busy = "false";
            // indicator.visibility = "collapsed";
            loader.hide();
            var options = {
                title: "Form Error",
                message: "Sorry an error occured",
                okButtonText: "OK"
            };
            dialogs.alert(options);
            console.log("url error");
            console.log(JSON.stringify(error));


        })

    }

}



//this function handles the major login, thats after user has ordered for an OTP and inputed it
exports.execLogin = function() {


    var username = page.getViewById("user_email");
    var password = page.getViewById("user_pass");
    console.log(password.text);

    if (validate("username", username.text) != true || validate("email", username.text) != true && validate("password", password.text) != true) {
        // if (validate("email", username.text) != true || validate("username", username.text) != true && validate("password", password.text) != true) {

        loader.hide();
        console.log("form error");
        var options = {
            title: "Form Error",
            message: "Invalid Password",
            okButtonText: "OK"
        };
        dialogs.alert(options).then(() => {
            console.log("password is invalid!");
        });

    } else {
        loader.show();
        Http.request({
            url: 'https://api.intelijence.com/paymiumm/login',
            method: "POST",
            headers: { "Content-Type": "application/json" },
            content: JSON.stringify({ "usr": username.text, "pwd": password.text })
        }).then(function(res) {
            //time for validation of response
            console.log(res);
            var res = res.content.toJSON();
            console.log(res['res']);
            console.log(res['userId']);
            console.log(res['user']);
            loader.hide();

            if (res['res']=="true") {

                
                //set device token


            //redirect user to home page
            
                // console.log(res['t_k_n_t_R'])
                // if(validateToken(res['t_k_n_t_R'])){

                    sessionStorage.setItem('loggedIn', true);
                    sessionStorage.setItem('loggedUser', username.text);
                    console.log("username is: " + sessionStorage.getItem("loggedUser"));
                    var loadHome = {
                        moduleName: 'pages/home/home',
                        context: { user: sessionStorage.getItem("loggedUser") },
                        clearHistory: true,
                        backstackVisible: false
                    }

                    page.closeModal();
                    frameModule.topmost().navigate(loadHome);


                // }

                // else{

                //     var options = {
                //         title: "Device Error",
                //         message: "Sorry your device id token mismatched with our records, check if your connection is secured",
                //         okButtonText: "OK"
                //     };
                //     dialogs.alert(options);


                // }

                //end of redirection

            } else if (res['res']=="accountUnconfirmed") {



                // if(validateToken(res['t_k_n_t_R'])){
                    console.log("not confirmed");
                    console.log(res['t_k_n_t_R'])
                    sessionStorage.setItem('loggedIn', true);
                    sessionStorage.setItem('loggedUser', username.text);
                    localStorage.setItem('date', res['da_t_e']);
                    console.log("username is: " + sessionStorage.getItem("loggedUser"));
                    var loadHome = {
                        moduleName: 'pages/personal/personal',
                        context: { user: sessionStorage.getItem("loggedUser") },
                        clearHistory: true,
                        backstackVisible: false
                    }

                    page.closeModal();
                    frameModule.topmost().navigate(loadHome);
                // }

                // else{

                //     var options = {
                //         title: "Device Error",
                //         message: "Sorry your device id token mismatched with our records, check if your connection is secured",
                //         okButtonText: "OK"
                //     };
                //     dialogs.alert(options);


                // }

                //end of redirection


            }
             else if (res['res']=="unconfirmed") {

                //account hasn't been confirmed throw error
                var options = {
                    title: "Form Error",
                    message: "Please confirm your email, before you can login",
                    okButtonText: "OK"
                };
                dialogs.alert(options);

            } else {

                //password was incorrect throw error
                var options = {
                    title: "Form Error",
                    message: "Incorrect OTP [code]",
                    okButtonText: "OK"
                };
                dialogs.alert(options);


            }
            console.log("form submitted");
            // console.log(res);

        }, function(error) {

            loader.hide();
            var options = {
                title: "Form Error",
                message: "Sorry an error occured",
                okButtonText: "OK"
            };
            dialogs.alert(options);
            console.log("url error");
            console.log(JSON.stringify(error));

        });

    }

}





function generateToken(token){
    var documents = fs.knownFolders.documents();
    var path = fs.path.join(documents.path, "/none/empty/device/identity/access/token/tokenReserve/tokenizer.tz");
    var file = fs.File.fromPath(path);

    // Writing text to the file.
    file.writeText(token.toString())
        .then(function () {
            // Succeeded writing to the file.
            console.log("done");
        }, function (error) {
            // Failed to write to the file.
            console.log(error);

        });
}


function validateToken(tknIza){
    var documents = fs.knownFolders.documents();
    var tokenFile = documents.getFile("/none/empty/device/identity/access/token/tokenReserve/tokenizer.tz");
    tokenFile.readText()
            .then(function (content) {
                console.log(content);
                console.log(tknIza)
                if (tknIza==content) {
                    console.log("true");
                    return true;
                }
                else{
                    console.log("false");
                    return false;
                }
                // Successfully read the file's content.
            }, function (error) {
                // Failed to read from the file.
                return false;
                console.log(error);
            });    

}
