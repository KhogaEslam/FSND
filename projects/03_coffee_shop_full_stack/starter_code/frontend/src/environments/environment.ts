export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'khogaeslam.eu', // the auth0 domain prefix of [https://khogaeslam.eu.auth0.com/]
    audience: 'cofee_shop', // the audience set for the auth0 app
    clientId: 'KmJ8F3Ha0qf0xAH7WjYGpkFjI1xVsBdG', //'47UoIs0dwpG73CjN4kCsEJ1GV22vM1op', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
