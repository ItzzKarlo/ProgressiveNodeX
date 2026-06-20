<script>
  const name = "SvelteKit";
</script>

<main>
  <p>ProgressiveNodeX</p>
  <h1>{name} starter</h1>
  <span>Edit <code>src/routes/+page.svelte</code>.</span>
</main>

<style>
  main {
    min-height: 100vh;
    display: grid;
    place-content: center;
    gap: 12px;
    font-family: Inter, system-ui, Arial, sans-serif;
    background: #0f172a;
    color: white;
  }

  h1 {
    font-size: clamp(3rem, 8vw, 6rem);
    margin: 0;
  }

  p {
    color: #fb7185;
    font-weight: 700;
  }
</style>