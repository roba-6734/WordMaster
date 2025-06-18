const API_BASE_URL = 'http://localhost:5000'

class ApiService {
    constructor(){
        this.token = localStorage.getItem('AuthToken')

    }

    setToken(token){
        this.token = token
        if (token){
            localStorage.setItem('AuthToken',token)
        }
        else{
            localStorage.removeItem('AuthToken')
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
        console.log('inside login before fetch')
        const response= await fetch(`${API_BASE_URL}/api/auth/login`,{
            method:'POST',
            headers:this.getHeaders(),
            body:JSON.stringify({
                email,
                password
            })

        })
        const data  = await response.json();
        console.log("we got data, this is the data")
        if (response.ok && data.access_token){
            this.setToken(data.access_token);
            console.log('we are fetching user data and it was successful')

            return {
                success:true,
                user:data,
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
    async getStats(){
        try{
        const response = await fetch(`${API_BASE_URL}/api/progress/stats`,{
            headers:this.getHeaders()
        })
        if(response.ok){
            return response.json()
        }
     }
        catch(error){
            throw new Error(error.detail || "Failed to fetch user stats")
        }
        
    }
    async getWords(pageNo=1,wordPerPage=20,searchTerm=''){
        const queryParams = new URLSearchParams({
      page: pageNo,
      per_page: wordPerPage,
      search: searchTerm
    }).toString();
        try{
            console.log("Trying to get words")
            const response = await fetch(`${API_BASE_URL}/api/words?${queryParams}`,{
                method:'GET',
                headers:this.getHeaders()})

            
           if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Error fetching words');
            }
            return response.json();

        }catch(error){
            console.log(error)
            throw new Error(error.message || "Failed to fetch words")
        }
    }

    async addWord(word){
        try{
            const response = await fetch(`${API_BASE_URL}/api/words/`,{
                method:'POST',
                headers:this.getHeaders(),
                body:JSON.stringify({
                    word
                })
            });
            if(!response.ok){
                const errorData = await response.json();
                throw new Error(errorData.message || 'Error fetching words');
            }
            console.log(response)
            return response.json()


        }catch(error){
            throw new Error(error.message || "Failed to add the word")
        }
    }

    logout(){
        this.setToken(null)
    }


}
const apiService = new ApiService()

export default apiService