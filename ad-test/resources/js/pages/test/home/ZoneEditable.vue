<template>
  <!--actualizado para modificar el bg si es > 5 distribuciones-->
  <div :class="['zone-editable', {'bg-success': form.distributions.length >= 5 && !editing}]">
    <div v-if="display" class="zone-display">
      <div>
        <!--Actualizado para agregar el campo ded fecha de actualizacion-->
        Zone Name: <strong>{{ name }}</strong> Distributions: {{ distributionDisplay }} <br>
        (Updated at: {{ form.updated_at }})
      </div>
      <button class="btn btn-primary" @click="setDisplay(false)" :disabled="saving">
        Edit
      </button>
    </div>

    <!--Formulario editable-->
    <div v-else class="zone-edit">
      <label class="control-label">Zone Name</label>
      <input v-model="form.name" placeholder="Zone name" class="form-control" :disabled="saving">

      <div class="zone-edit-distributions">
        <!--identifico por key-->
        <div v-for="(distribution, index) in form.distributions" :key="index">
          <label class="control-label">Distribution</label>
          <input v-model="distribution.percentage" placeholder="Percentage" class="form-control">
          <!--% dentro de la edicion dinamico-->
          <span v-if="!editing" @click="startEditing(distribution)">{{ distribution.percentage }}%</span>
        </div>
      </div>

      <!--Zona de botones/acciones-->
      <div class="zone-edit-actions">
        <button class="btn btn-danger" @click="cancel" :disabled="saving">
          Cancel
        </button>

        <!--Boton guardar actualizado con el % de guardado-->
        <button class="btn btn-success" @click="save" :disabled="saving || totalPercent !== 100">
          <span v-if="!saving">Save</span>
          <span v-else>Saving...</span>
        </button>

        <!--Botones agregar y remover-->
        <button class="btn btn-primary" @click="addDistribution" :disabled="saving">
          Add
        </button>

        <button class="btn btn-remover" @click="removeDistribution" :disabled="saving">
          Remove
        </button>
      </div>
    </div>
    <!--Zona de errores-->
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>

    <div v-if="showErrors" class="alert alert-danger">{{ error }}</div>

  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ZoneEditable',
  props: {
    name: String,
    id: Number,
    distributions: Array,
    updated_at: String,//lo agrego como cadena de texto
  },
  data() {
    return {
      display: true,
      editing: false,
      showErrors: false,
      editingDistribution: null,
      successMessage: '',

      form: {
        name: '',
        distributions: JSON.parse(JSON.stringify(this.distributions)),//lo convierto en json para separar las referencias.
        updated_at: '',
       
        newDistributions: [],//creo un campo de arreglo, para que los nuevos dist se agreguen
      },
      saving: false,
    };
  },

  computed: {
    distributionDisplay() {
      return this.form.distributions.map(distribution => distribution.percentage + '%').join('-');
    },
    totalPercent() {
      return this.form.distributions.reduce((total, distribution) => total + parseFloat(distribution.percentage), 0);
    },
  },

  mounted() {
    this.getValuesFromProps();
    this.form.updated_at = this.updated_at;

    // cargar los datos
    axios
      .get(`api/zones/${this.id}`)
      .then(response => {
        const updatedData = response.data;

        // update a las distribuciones existentes y nuevas desde el backend
        const existingDistributionsIds = new Set(this.form.distributions.map(distribution => distribution.id));
        const updatedDistributions = updatedData.distributions.map(distribution => ({ ...distribution }));

        updatedDistributions.forEach(distribution => {
          if (existingDistributionsIds.has(distribution.id)) {
            // Actualizar distribuciones existentes
            const existingDistribution = this.form.distributions.find(d => d.id === distribution.id);
            if (existingDistribution) {
              Object.assign(existingDistribution, distribution);
            }
          } else{
            // Agregar nuevas distribuciones al formulario
            this.form.newDistributions.push({ ...distribution });
          }
        });

        // Limpiar inexistentes
        this.form.distributions = this.form.distributions.filter(distribution => existingDistributionsIds.has(distribution.id));

        // Limpiar  nuevos campos de distribución
        this.form.newDistributions = [];

        this.form.name = updatedData.name;
        this.form.updated_at = updatedData.updated_at;
      })
      .catch(error => {
        console.error('Error while fetching data:', error);
      });
  
  
  },
  //INICIAN LOS METODOS
  methods: {
    getValuesFromProps() {
      this.form.name = this.name;
      this.form.distributions = this.distributions.map(distribution => ({ ...distribution }));
    },
    setDisplay(value) {
      this.display = value;
      if (!this.display) {
        this.getValuesFromProps();
        this.error = null;
      }
    },
    //iniciar edicion
    startEditing(distribution) {
      this.editingDistribution = { ...distribution };
     
    },
    //guardar actualizado
    async save() {
      this.showErrors = false;
      this.validate();
      if (this.hasErrors) {
        this.showErrors = true;
        return;
      }
      this.saving = true;
      const params = {
        id: this.id,
        name: this.form.name,
        distributions: this.form.distributions,
        newDistributions: this.form.newDistributions, // Agrego newDistributions como parámetro aparte
        updated_at: new Date().toISOString(), 
      };

      //validacion de ID para distributions:
      this.form.distributions.forEach((distribution, index) => {
          if(distribution.id === undefined){
           // distribution = null; //aqui indicamos que si no tiene un id, le coloque null, para que django lo asigne al enviar.
          ///la opcion anterior no funciono, ya que solo se agrega a la variable local, por tanto hare pruebas con el indice:
          distribution = null;
          }
        });

      try {
          console.log('Datos enviados al backend:', params);
          await axios.post('api/zones/edit', params); // Enviar datos al backend
          const response = await axios.get(`api/zones/${this.id}`); // Obtener los datos actualizados 
          const updatedData = response.data;

          // Actualizar 
          this.form.name = updatedData.name;
          this.form.distributions = updatedData.distributions.map(distribution => ({ ...distribution }));
          this.form.updated_at = updatedData.updated_at;
          this.form.editing = false;
          this.form.newDistributions = []; // Limpiar los  campos 

          this.successMessage = 'Saved successfully';
          setTimeout(() => {
            this.successMessage = '';
          }, 3000);

          this.display = true;
          this.showErrors = false;
        } catch (error) {
          this.error = 'Error on saving, please try again.';
          this.saving = false;
          this.showErrors = false;
        } finally {
          this.saving = false;
      }
    },
    //metodo cancelar, se habilito el boton, y  se agrego la funcionalidad
    async cancel() {
      this.display = true;
      this.form.name = this.name;
      this.form.distributions = JSON.parse(JSON.stringify(this.distributions));
      this.form.newDistributions = [];
      this.error = null;
      this.hasErrors = false;
      this.showErrors = false;
    },
    //metodo para agregar distribuciones
    async addDistribution() {
      if (this.editingDistribution !== null) {
        const editedIndex = this.form.distributions.findIndex(
          distribution => distribution.id === this.editingDistribution.id);
        if (editedIndex !== -1) {
          this.form.distributions.splice(editedIndex, 1, this.editingDistribution);
          this.editingDistribution = null; // Reinicia el estado de edición
          this.form.editing = false; // Finaliza el modo de edición
        }
      }else{
        const newDistribution = { percentage: 0 };
        this.form.distributions.push(newDistribution);
       }
    },
    //metodo para remover distribuciones
    removeDistribution(index) {
      if (this.form.distributions.length > 1) {
        this.form.distributions.splice(index, 1);//las elimino de acuerdo a su indice
      }
    },
    //metodo para validar los errores:
    async validate() {
      this.showErrors = true;
      this.hasErrors = false; // cambiamos a false
      //porcentaje a 100
      const totalPercentage = this.form.distributions.reduce((total, distribution) => total + parseFloat(distribution.percentage), 0);
      if (totalPercentage !== 100) {
        this.error = 'The percentage has to be equal to 100%.';
        this.hasErrors = true;
        return;
      }
      //numeros enteros
      for (const distribution of this.form.distributions) {
        if (distribution.percentage % 1 !== 0) {
          this.error = 'Must be Integer Numbers, please try again.';
          this.hasErrors = true;
          return;
        }
      }
      //no zonas vacias
      if (this.form.name.trim() === '') {
        this.error = "The Zone Name can't be empty, please try again.";
        this.hasErrors = true;
        return;
      }
      //sin mas de 1 spacio entre palabras
      if (/\s{2}/.test(this.form.name)) {
        this.error = 'The name cannot have more than 1 space between words, please try again.';
        this.hasErrors = true;
        return;
      }
      //la zona sin espacio al frente
      if (/^\s|\s$/.test(this.form.name)) {
        this.error = 'The Zone name cannot have leading or trailing spaces, please try again.';
        this.hasErrors = true;
        return;
      }
      // Nombres unicos
      const zoneNames = this.$parent.zones.map(zone => zone.name.toLowerCase()); // busco todos los nombres de zonas
      const editedZoneName = this.form.name.toLowerCase(); // reviso el nombre activo de zona (en minuscula por propiedad lowerCase)
      const editedZoneIndex = zoneNames.indexOf(editedZoneName); // valido si existe en la lista
      //si estoy editando
      if (editedZoneIndex !== -1 && this.$parent.zones[editedZoneIndex].id !== this.id) {
        // Si el nombre de la zona en edición existe en otro registro (y no es el registro actual que estamos editando)
        this.error = 'The Zone name must be unique, please try again.';
        this.hasErrors = true;
        return;
      }
    },

    async refreshForm(data) {
      this.form.name = data.name;
      this.form.distributions = data.distributions.map(distribution => ({ ...distribution }));
      this.form.updated_at = data.updated_at; 
      this.form.editing = false;
      
      this.showErrors = false;
    },
  },
};
</script>

<style lang="scss">
@import 'resources/scss/variables.scss';

.zone-editable {
  border: 1px solid $gray-color;
  padding: $qmb;
  border-radius: $border-radius;

  .zone-display {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .zone-edit {
    display: flex;
    flex-direction: column;
    gap: $small-action-space;

    .zone-edit-actions {
      display: flex;
      gap: $small-action-space;
      justify-content: end;
    }

    .zone-edit-distributions {
      display: grid;
      grid-template-columns: repeat(1, 1fr);
      gap: $small-action-space;
    }
  }

  .btn-remover {
    /* Estilos específicos para el botón "remover" */
    background-color: #ff8000; /* Naranja */
    color: #efeeee;
}
}
</style>
