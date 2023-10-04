clear
clc

xi=0.00001;
tau=1.5;

n=4096;
dt=0.01;
t=(0:n-1)*dt;

s=t.^xi.*exp(-t./tau);
h=heaviside(tau-t).*sin(t*pi/tau);
ss=conv(s,h)

%[f,S,dummy]=FFT(s,dt);

figure(1)
plot(t,ss(1:n),'k',t,h,'r')

%figure(2)
%loglog(f,S)
