const API = "http://127.0.0.1:8000"

window.onload = function() {
    const token = localStorage.getItem("token")
    const rol = localStorage.getItem("rol")
    if (token) {
        if (rol === "profesional") {
            mostrarBotonesLogueadoProfesional()
            mostrarSeccion('citas_profesional')
        } else {
            mostrarBotonesLogueado()
            mostrarSeccion('disponibilidad')
        }
    }
}

document.getElementById("formLoginProfesional").addEventListener("submit", async function(e) {
    e.preventDefault()
    
    const dni = document.getElementById("pro_login_dni").value
    const password = document.getElementById("pro_login_password").value
    
    const respuesta = await fetch(`${API}/login_profesional?dni=${dni}&password=${password}`, {
        method: "POST"
    })
    
    const datos = await respuesta.json()
    
    if (respuesta.ok) {
        localStorage.setItem("token", datos.access_token)
        localStorage.setItem("rol", "profesional")
        mostrarBotonesLogueadoProfesional()
        mostrarSeccion('citas_profesional')
    } else {
        alert(datos.detail)
    }
})

function mostrarBotonesLogueadoProfesional() {
    document.getElementById("btn_crear_horario").style.display = "inline"
    document.getElementById("btn_citas_profesional").style.display = "inline"
    document.getElementById("btn_cerrar_sesion").style.display = "inline"
    document.getElementById("btn_login").style.display = "none"
    document.getElementById("btn_login_profesional").style.display = "none"
    document.getElementById("btn_registro").style.display = "none"
}

function mostrarBotonesLogueado() {
    document.getElementById("btn_disponibilidad").style.display = "inline"
    document.getElementById("btn_mis_citas").style.display = "inline"
    document.getElementById("btn_cerrar_sesion").style.display = "inline"
    document.getElementById("btn_login").style.display = "none"
    document.getElementById("btn_login_profesional").style.display = "none"
    document.getElementById("btn_registro").style.display = "none"
}

function mostrarSeccion(id) {
    document.querySelectorAll('.seccion').forEach(div => div.style.display = 'none')
    document.getElementById(id).style.display = 'block'
    
    if (id === 'disponibilidad') {
        document.getElementById("fecha").min = new Date().toISOString().split("T")[0]
        cargarProfesionales()
    }
    if (id === 'mis_citas') {
        cargarMisCitas()
    }

    if (id === 'citas_profesional') {
    cargarCitasProfesional()
    }
}

function cerrarSesion() {
    localStorage.removeItem("token")
    localStorage.removeItem("rol")
    document.getElementById("btn_disponibilidad").style.display = "none"
    document.getElementById("btn_mis_citas").style.display = "none"
    document.getElementById("btn_cerrar_sesion").style.display = "none"
    document.getElementById("btn_crear_horario").style.display = "none"
    document.getElementById("btn_citas_profesional").style.display = "none" 
    document.getElementById("btn_login_profesional").style.display = "inline"
    document.getElementById("btn_login").style.display = "inline"
    document.getElementById("btn_registro").style.display = "inline"
    mostrarSeccion('login')
}

document.getElementById("formLogin").addEventListener("submit", async function(e) {
    e.preventDefault()
    
    const dni = document.getElementById("login_dni").value
    const password = document.getElementById("login_password").value
    
    const respuesta = await fetch(`${API}/login?dni=${dni}&password=${password}`, {
        method: "POST"
    })
    
    const datos = await respuesta.json()
    
    if (respuesta.ok) {
        localStorage.setItem("token", datos.access_token)
        localStorage.setItem("rol", "usuario")  // ← falta esto
        mostrarBotonesLogueado()
        mostrarSeccion('disponibilidad')
    }
    else {
        alert(datos.detail)
    }
})


async function cargarMisCitas() {
    const token = localStorage.getItem("token")

    const getdate = await fetch(`${API}/mis_citas`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`
        }
    })

    if (!getdate.ok) {
        const error = await getdate.json()
        alert(error.detail)
        return
    }

    const citas = await getdate.json()
    console.log("citas cargadas:")
    console.log(citas)

    mostrarCitas(citas)
}

function mostrarCitas(citas) {
    const lista = document.getElementById("lista_citas")
    lista.innerHTML = ""
    
    citas.forEach(cita => {
        const li = document.createElement("li")
        
        li.innerHTML = `
            ${cita.profesional} - ${cita.fecha} - ${cita.h_start} - ${cita.h_end} - ${cita.estado}
            ${cita.estado === "confirmada" ? 
                `<button onclick="cancelarCita(${cita.id})">Cancelar</button>` 
                : ""}
        `
        lista.appendChild(li)
    })
}

async function cargarProfesionales() {
    const respuesta = await fetch(`${API}/profesionales`)
    const profesionales = await respuesta.json()
    
    const datalist = document.getElementById("profesionales")
    datalist.innerHTML = ""
    
    profesionales.forEach(p => {
        const option = document.createElement("option")
        option.value = p.name
        option.dataset.dni = p.dni
        datalist.appendChild(option)
    })
}

document.getElementById("buscar_disponibilidad").addEventListener("click", async function() {
    const nombreElegido = document.getElementById("buscar_profesional").value
    const fecha = document.getElementById("fecha").value
    
    if (!fecha) {
        alert("Selecciona una fecha")
        return
    }

    const options = document.querySelectorAll("#profesionales option")
    let dni = null
    options.forEach(opt => {
        if (opt.value === nombreElegido) dni = opt.dataset.dni
    })
    
    if (!dni) {
        alert("Selecciona un profesional válido de la lista")
        return
    }

    const token = localStorage.getItem("token")
    const respuesta = await fetch(`${API}/disponibilidad?professional_dni=${dni}&fecha=${fecha}`, {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` }
    })

    if (!respuesta.ok) {
        const error = await respuesta.json()
        alert(error.detail)
        return
    }

    const datos = await respuesta.json()
    const slots = datos.slots_disponibles

    const lista = document.getElementById("lista_slots")
    lista.innerHTML = ""

    if (slots.length === 0) {
        lista.innerHTML = "<li>No hay slots disponibles para ese día</li>"
        return
    }

    slots.forEach(slot => {
        const li = document.createElement("li")
        const btn = document.createElement("button")
        btn.textContent = slot
        btn.onclick = () => crearCita(dni, fecha, slot)
        li.appendChild(btn)
        lista.appendChild(li)
    })
})

async function crearCita(professional_dni, fecha, h_start) {
    const token = localStorage.getItem("token")
    
    const respuesta = await fetch(`${API}/crear_appointment?professional_dni=${professional_dni}&fecha=${fecha}&h_start=${h_start}:00`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
    })

    const datos = await respuesta.json()

    if (respuesta.ok) {
        alert("¡Cita creada exitosamente!")
        document.getElementById("buscar_disponibilidad").click()
    } else {
        alert(datos.detail)
    }
}

async function cancelarCita(id_cita) {
    if (!confirm("¿Seguro que quieres cancelar esta cita?")) return
    
    const token = localStorage.getItem("token")
    
    const respuesta = await fetch(`${API}/cancelar_cita/${id_cita}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
    })
    
    const datos = await respuesta.json()
    
    if (respuesta.ok) {
        alert("Cita cancelada exitosamente")
        cargarMisCitas()  // recargar la lista
    } else {
        alert(datos.detail)
    }
}

document.getElementById("formCrearHorario").addEventListener("submit", async function(e) {
    e.preventDefault()
    
    const token = localStorage.getItem("token")
    const dia = document.getElementById("horario_dia").value
    const h_start = document.getElementById("horario_inicio").value + ":00"
    const h_end = document.getElementById("horario_fin").value + ":00"
    
    const respuesta = await fetch(`${API}/crear_p_horario?dia_semana=${dia}&h_start=${h_start}&h_end=${h_end}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
    })
    
    const datos = await respuesta.json()
    
    if (respuesta.ok) {
        alert("Horario guardado exitosamente")
    } else {
        alert(datos.detail)
    }
})

async function cargarCitasProfesional() {
    const token = localStorage.getItem("token")
    
    const respuesta = await fetch(`${API}/citas_profesional`, {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` }
    })

    const lista = document.getElementById("lista_citas_profesional")
    lista.innerHTML = ""

    if (!respuesta.ok) {
        lista.innerHTML = "<li>No hay citas registradas</li>"
        return
    }

    const citas = await respuesta.json()
    
    citas.forEach(cita => {
        const li = document.createElement("li")
        li.innerHTML = `${cita.paciente} - ${cita.fecha} - ${cita.h_start} - ${cita.h_end} - ${cita.estado}`
        lista.appendChild(li)
    })
}

