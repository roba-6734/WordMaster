const API_BASE_URL = 'http://localhost:5000'

class ApiService {
    constructor(){
        this.token = localStorage.getItem('AuthToken')

    }

    setToken(token){
        this.token = token
        if (token){
            localStorage.set('AuthToken',token)
        }
        else{
            localStorage.remove('AuthToken')
        }
    }

    getHeaders(){
        const header = { 
            'Content-Type':'application/json'
        }
        if(this.token){
            header.Authorization = `Bearer ${this.token}`
        }
        return header

    }
    
    async login(email,password){
        const response= await fetch(`${API_BASE_URL}/api/auth/login`,{
            methods:'POST',
            headers:this.getHeaders(),
            body:JSON.stringify({
                email,
                password
            })

        })
        const data  = await response.json();
        if (response.ok && data.access_token){
            this.setToken(data.access_token)
            return {
                success:true,
                token:data.access_token
            }
        }
        else{
            throw new Error(data.detail || "Login failed, please try again")
        }

    }

    async register(email,password,display_name){
        const response = await fetch(`${API_BASE_URL}/api/auth/register`,{
            method:'POST',
            headers:this.getHeaders(),
            body: JSON.stringify({
                email,
                password,
                display_name
            })

        })

        const data = await response.json()
        if(response.ok ){
            return {
                success:true,
                user:data
            }
        }else{
            throw new Error(data.detail || 'Registration failed')
        }

    }

    async getUserData(){
        const response = await fetch(`${API_BASE_URL}/api/auth/user`,{
            method:'GET',
            headers:this.getHeaders(),

        })
        if(response.ok){
            return response.json()
        }else{
            throw new Error(response.detail || "Failed to get user info")
        }

    }

    logout(){
        this.setToken(null)
    }

}
const apiService = new ApiService()

export default apiService