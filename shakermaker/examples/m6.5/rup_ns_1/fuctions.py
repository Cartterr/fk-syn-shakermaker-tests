import numpy as np

def Integral_directa(ug,dtac,dt,w,nu,uo,vo): #retorna la integral de p(t) entre 0 y vectort[-1] por el método de Trapecio
    #print("Piese wise linear")   
    #variables 
    n=len(ug)
    ug2 = ug
    ug = []
    for i in ug2:
        ug.append(-i)
        
    nn=int(dtac/dt)
    wd=w*np.sqrt(1-nu**2)
    u=np.zeros((n*nn))
    v=u
    
    u[0] = uo
    v[0] = vo
    
    A = np.exp(-nu*w*dt) * (nu/np.sqrt(1-nu**2) * np.sin(wd*dt)+np.cos(wd*dt))
    B = np.exp(-nu*w*dt) * (1/wd*np.sin(wd*dt))
    C = ((1-2*nu**2)/(wd*dt) - nu/np.sqrt(1-nu**2)) * np.sin(wd*dt)-(1+2*nu/(w*dt)) * np.cos(wd*dt)
    C = 1/w**2*(2*nu/(w*dt) + np.exp(-nu*w*dt)*C)
    D = (2*nu**2-1)/(wd*dt) * np.sin(wd*dt)+2*nu/(w*dt) * np.cos(wd*dt)
    D = 1/w**2*(1-2*nu/(w*dt) + np.exp(-nu*w*dt)*D)
    A1 = -np.exp(-nu*w*dt) * (w/np.sqrt(1-nu**2) * np.sin(wd*dt))
    B1 = np.exp(-nu*w*dt) * (np.cos(wd*dt) - nu/np.sqrt(1-nu**2) * np.sin(wd*dt))
    C1 = (w/np.sqrt(1-nu**2) + nu/(dt*np.sqrt(1-nu**2))) * np.sin(wd*dt)+1/dt*np.cos(wd*dt)
    C1 = 1/w**2 * (-1/dt+np.exp(-nu*w*dt)*C1)
    D1 = 1/w**2/dt * (1-np.exp(-nu*w*dt) * (nu/np.sqrt(1-nu**2) * np.sin(wd*dt) + np.cos(wd*dt)))
        
    ii=0
    for i in range(n-1):
        dg=(ug[i+1]-ug[i])/nn
        
        for j in range(nn):
            ace1= ug[i] + (j) * dg
            ace2= ug[i] + (j+1) * dg  
            u[ii+1]= A*u[ii] + B*v[ii] + C*ace1 + D*ace2
            v[ii+1]= A1*u[ii] + B1*v[ii] + C1*ace1 + D1*ace2
            ii=ii+1
          
    return u,v

def piece_wise_linear2(vector_a,w,chi): #retorna la integral de p(t) entre 0 y vectort[-1] por el método de Trapecio
    #print("Piese wise linear")   
    #variables 
    h = 0.005
    u_t = [0.]
    up_t = [0.]
    upp_t = [0.]
    m = 1
    w_d = w*np.sqrt(1-chi**2) #1/s 
    
    sin = np.sin(w_d*h)
    cos = np.cos(w_d*h)
    e = np.exp(-chi*w*h)
    raiz = np.sqrt(1-chi**2)
    división = 2*chi/(w*h)
    
    A = e * (chi*sin/raiz+cos) #check
    B = e * (sin/w_d) #check
    C = (1/w**2) * (división  + e * (((1 - (2*chi**2))/(w_d*h) - chi/raiz)*sin - (1+división)*cos)) #check
    D = (1/w**2) * (1-división + e * ((2*chi**2-1)*sin/(w_d*h)+división*cos)) #check
    
    A1 = -e * ((w*sin)/raiz) #check
    B1 =  e * ( cos - chi*sin/raiz  ) #check
    C1 = (1/w**2) * (- 1/h + e*((w/raiz + chi/(h*raiz) ) * sin + cos/h)) #check 
    D1 = (1/w**2) * (1/h - (e/h*( chi*sin/raiz + cos   ))) #check
    
    vector_a.insert(0,0)
    
    for i in range(len(vector_a)-1):
        pi = -(vector_a[i])*m#pi
        pi1 = -(vector_a[i+1])*m #pi+1
        
        ui = u_t[i] #u_i(t)
        vi = up_t[i] #v_i(t)
        ui1 = A*ui + B*vi + C*pi + D*pi1 #u_i+1
        upi1 = A1*ui + B1*vi + C1*pi + D1*pi1 #up_i+1 
        
        u_t.append(ui1)
        up_t.append(upi1)
        
    vector_a.pop(0)
    u_t.pop(0)
    up_t.pop(0)
    upp_t.pop(0)
    
    return u_t,up_t
