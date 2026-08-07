export const timeAgo=dt=>{if(!dt)return '';const s=Math.floor((Date.now()-new Date(dt))/1000);if(s<60)return 'just now';if(s<3600)return `${Math.floor(s/60)}m ago`;if(s<86400)return `${Math.floor(s/3600)}h ago`;return `${Math.floor(s/86400)}d ago`}
export const fmtDate=(dt,opts)=>dt?new Date(dt).toLocaleDateString('en-GB',opts||{day:'numeric',month:'short',year:'numeric'}):''
export const fmtTime=dt=>dt?new Date(dt).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}):''
export const fmtDateTime=dt=>dt?`${fmtDate(dt)} ${fmtTime(dt)}`:''
export const fmtDay=dt=>dt?new Date(dt).getDate():''
export const fmtMonth=dt=>dt?new Date(dt).toLocaleString('default',{month:'short'}):''
export const fmtCurrency=(amt,cur='GHS')=>`${cur} ${parseFloat(amt||0).toFixed(2)}`
export const statusBadge=s=>({pending:'bg-warning-subtle text-warning',confirmed:'bg-success-subtle text-success',in_progress:'bg-primary-subtle text-primary',completed:'bg-secondary-subtle text-secondary',cancelled:'bg-danger-subtle text-danger',no_show:'bg-dark-subtle text-dark',rescheduled:'bg-info-subtle text-info',approved:'bg-success-subtle text-success',rejected:'bg-danger-subtle text-danger',suspended:'bg-warning-subtle text-warning'}[s]||'bg-light text-muted')
export const truncate=(str,len=100)=>(!str?'':str.length>len?str.slice(0,len)+'…':str)
export const debounce=(fn,delay=350)=>{let t;return(...a)=>{clearTimeout(t);t=setTimeout(()=>fn(...a),delay)}}
export const getInitials=(name='')=>name.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase()
export const avatarUrl=user=>user?.avatar_url||`https://ui-avatars.com/api/?name=${encodeURIComponent(user?.full_name||'User')}&background=e63900&color=fff`
export const methodLabel=m=>({card:'Card',mtn_momo:'MTN MoMo',at_momo:'AirtelTigo',tel_cash:'Telecel Cash',bank:'Bank',wallet:'Wallet'}[m]||m)
export const notifIcon=type=>({lesson_booked:'bi-calendar-check-fill',lesson_reminder:'bi-alarm-fill',lesson_started:'bi-camera-video-fill',lesson_completed:'bi-check-circle-fill',lesson_cancelled:'bi-calendar-x-fill',payment_received:'bi-cash-coin',review_received:'bi-star-fill',message_received:'bi-chat-dots-fill',system:'bi-info-circle-fill'}[type]||'bi-bell-fill')
