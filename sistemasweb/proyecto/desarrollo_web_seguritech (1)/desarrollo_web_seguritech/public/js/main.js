document.addEventListener('DOMContentLoaded', function() {
  initForm();

  // Dashboard: cargar datos y configurar botón reintentar
  if (document.getElementById('dashboardContent')) {
    loadDashboard();

    var btnReintentar = document.getElementById('btnReintentar');
    if (btnReintentar) {
      btnReintentar.addEventListener('click', function(e) {
        e.preventDefault();
        loadDashboard();
      });
    }
  }

  if (document.getElementById('ajaxServicios')) {
    cargarServiciosFiltro();
  }
});

function initForm() {
  var form = document.getElementById('solicitudForm');
  if (!form) return;

  form.addEventListener('submit', function(e) {
    var ok = true;
    var fields = ['nombre', 'email', 'telefono', 'servicio_id', 'mensaje'];

    for (var i = 0; i < fields.length; i++) {
      var el = document.getElementById(fields[i]);
      if (!el) continue;
      var val = el.value.trim();
      var valid = true;

      if (fields[i] === 'nombre' && val.length < 3) valid = false;
      if (fields[i] === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) valid = false;
      if (fields[i] === 'telefono' && val.length < 7) valid = false;
      if (fields[i] === 'servicio_id' && !val) valid = false;
      if (fields[i] === 'mensaje' && val.length < 10) valid = false;

      if (!valid) {
        el.classList.add('is-invalid');
        ok = false;
      } else {
        el.classList.remove('is-invalid');
      }
    }

    if (!ok) {
      e.preventDefault();
      var first = form.querySelector('.is-invalid');
      if (first) {
        first.scrollIntoView({
          behavior: 'smooth', block: 'center'
        });
      }
    } else {
      e.preventDefault();
      enviarFormularioAjax(form);
    }
  });

  var inputs = form.querySelectorAll('input, select, textarea');
  for (var j = 0; j < inputs.length; j++) {
    inputs[j].addEventListener('input', function() {
      this.classList.remove('is-invalid');
    });
  }
}

async function enviarFormularioAjax(form) {
  var btn = document.getElementById('btnSubmit');
  var spinner = document.getElementById('loadingSpinner');

  try {
    if (btn) btn.disabled = true;
    if (spinner) spinner.classList.remove('d-none');
    var formData = new FormData(form);
    const response = await fetch('/solicitud', {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: formData
    });

    const resultado = await response.json();
    if (!response.ok || !resultado.success) {
      throw resultado;
    }

    mostrarMensaje(
      'Solicitud enviada correctamente. Folio #' + resultado.id,
      'success'
    );

    form.reset();
  } catch (error) {
    if (error.errores) {
      mostrarMensaje(
        error.errores.join('<br>'),
        'danger'
      );
    } else {
      mostrarMensaje(
        'Error al enviar la solicitud.',
        'danger'
      );
    }
  } finally {
    if (btn) btn.disabled = false;
    if (spinner) spinner.classList.add('d-none');
  }
}

function mostrarMensaje(texto, tipo) {
  var anterior = document.getElementById('mensajeAjax');

  if (anterior) {
    anterior.remove();
  }

  var div = document.createElement('div');
  div.id = 'mensajeAjax';
  div.className = 'alert alert-' + tipo + ' mt-3';
  div.innerHTML = texto;
  var form = document.getElementById('solicitudForm');
  form.prepend(div);

  setTimeout(function() {
    div.remove();
  }, 5000);
}

function selectService(id) {
  var sel = document.getElementById('servicio_id');
  if (sel) {
    sel.value = id;
    sel.classList.remove('is-invalid');
    var contacto = document.getElementById('contacto');
    if (contacto) contacto.scrollIntoView({behavior: 'smooth'});
  }
}

function loadDashboard() {
  var loading = document.getElementById('loadingDashboard');
  var content = document.getElementById('dashboardContent');
  var error = document.getElementById('dashboardError');

  if (loading) loading.classList.remove('d-none');
  if (content) content.classList.add('d-none');
  if (error) error.classList.add('d-none');

  fetch('/api/dashboard/data')
    .then(function(res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    })
    .then(function(json) {
      if (json.success) {
        renderDashboard(json.data);
        if (loading) loading.classList.add('d-none');
        if (content) {
          content.classList.remove('d-none');
          content.classList.add('fade-in');
        }
      } else {
        throw new Error('Datos invalidos');
      }
    })
    .catch(function(err) {
      console.error(err);
      if (loading) loading.classList.add('d-none');
      if (error) error.classList.remove('d-none');
    });
}

function renderDashboard(data) {
  var kpiTotal = document.getElementById('kpiTotalSolicitudes');
  var kpiServ = document.getElementById('kpiTotalServicios');
  var kpiTop = document.getElementById('kpiServicioTop');
  var kpiPen = document.getElementById('kpiPendientes');

  if (kpiTotal) kpiTotal.textContent = data.totalSolicitudes || 0;
  if (kpiServ) kpiServ.textContent = data.totalServicios || 0;
  if (kpiTop) {
    kpiTop.textContent = data.servicioMasPedido ? data.servicioMasPedido.nombre : '-';
    kpiTop.title = kpiTop.textContent;
  }

  var pen = null;
  if (data.estados) {
    for (var i = 0; i < data.estados.length; i++) {
      if (data.estados[i].estado === 'pendiente') {
        pen = data.estados[i];
        break;
      }
    }
  }
  if (kpiPen) kpiPen.textContent = pen ? pen.total : 0;

  // Estados
  var estadosDiv = document.getElementById('estadosContainer');
  if (estadosDiv && data.estados) {
    var labels = { pendiente: 'Pendiente', en_proceso: 'En Proceso', completada: 'Completada', cancelada: 'Cancelada' };
    var classes = { pendiente: 'bg-warning', en_proceso: 'bg-primary', completada: 'bg-success', cancelada: 'bg-danger' };
    var total = data.totalSolicitudes || 1;
    var html = '';
    for (var e = 0; e < data.estados.length; e++) {
      var est = data.estados[e];
      var pct = ((est.total / total) * 100).toFixed(1);
      html += '<div class="mb-2"><div class="d-flex justify-content-between small"><span>' + (labels[est.estado] || est.estado) + '</span><span class="text-muted">' + est.total + ' (' + pct + '%)</span></div><div class="progress"><div class="progress-bar ' + (classes[est.estado] || 'bg-secondary') + '" style="width:' + pct + '%"></div></div></div>';
    }
    estadosDiv.innerHTML = html;
  }

  // Servicios
  var serviciosDiv = document.getElementById('serviciosContainer');
  if (serviciosDiv && data.solicitudesPorServicio) {
    var maxVal = 1;
    for (var s = 0; s < data.solicitudesPorServicio.length; s++) {
      if (data.solicitudesPorServicio[s].total > maxVal) maxVal = data.solicitudesPorServicio[s].total;
    }
    var colors = ['bg-primary', 'bg-success', 'bg-info', 'bg-warning', 'bg-danger'];
    var html2 = '';
    for (var s2 = 0; s2 < data.solicitudesPorServicio.length; s2++) {
      var serv = data.solicitudesPorServicio[s2];
      var pct2 = ((serv.total / maxVal) * 100).toFixed(1);
      html2 += '<div class="mb-2"><div class="d-flex justify-content-between small"><span class="text-truncate" style="max-width:70%">' + esc(serv.nombre) + '</span><span class="text-muted">' + serv.total + '</span></div><div class="progress"><div class="progress-bar ' + colors[s2 % colors.length] + '" style="width:' + pct2 + '%"></div></div></div>';
    }
    serviciosDiv.innerHTML = html2;
  }

  // Tabla
  var tbody = document.getElementById('tbodySolicitudes');
  if (tbody && data.ultimasSolicitudes) {
    var ec = { pendiente: 'bg-warning text-dark', en_proceso: 'bg-primary', completada: 'bg-success', cancelada: 'bg-danger' };
    var el = { pendiente: 'Pendiente', en_proceso: 'En Proceso', completada: 'Completada', cancelada: 'Cancelada' };
    var html3 = '';
    for (var u = 0; u < data.ultimasSolicitudes.length; u++) {
      var sol = data.ultimasSolicitudes[u];
      html3 += '<tr><td>#' + sol.id + '</td><td>' + esc(sol.nombre) + '</td><td>' + esc(sol.servicio_nombre) + '</td><td><span class="badge ' + (ec[sol.estado] || 'bg-secondary') + '">' + (el[sol.estado] || sol.estado) + '</span></td><td>' + fmt(sol.fecha) + '</td></tr>';
    }
    tbody.innerHTML = html3;
  }
}

function esc(t) {
  if (!t) return '';
  var d = document.createElement('div');
  d.textContent = t;
  return d.innerHTML;
}

function fmt(ds) {
  if (!ds) return '-';
  var d = new Date(ds);
  return d.toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' });
}

function cargarServiciosFiltro() {
  const contenedor = document.getElementById('ajaxServicios');
  if (!contenedor) return;

  fetch('/api/servicios')
    .then(res => res.json())
    .then(json => {
      contenedor.innerHTML = '';

      json.data.forEach(s => {
        contenedor.innerHTML += `
          <div class="col-md-6 col-lg-4 servicio-item" data-categoria="${s.categoria_id}">
            <div class="card service-card h-100">
              <div class="card-body">
                <span class="badge bg-success">${s.categoria_nombre}</span>
                <h5>${s.nombre}</h5>
                <p>${s.descripcion}</p>
                <a href="/contacto" class="btn btn-primary">Solicitar</a>
              </div>
            </div>
          </div>
        `;
      });

      activarFiltros();
    })
    .catch(err => {
      console.error('Error servicios:', err);
      contenedor.innerHTML = `
        <div class="alert alert-danger">
          No fue posible cargar los servicios.
        </div>
      `;
    });
}

function activarFiltros() {
  const botones = document.querySelectorAll('.btn-filtro');
  const servicios = document.querySelectorAll('.servicio-item');

  botones.forEach(btn => {
    btn.addEventListener('click', () => {
      let categoria = btn.dataset.categoria;

      servicios.forEach(serv => {
        if (categoria === "0" || serv.dataset.categoria === categoria) {
          serv.style.display = "";
        } else {
          serv.style.display = "none";
        }
      });
    });
  });
}
