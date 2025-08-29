<div class="splash-screen">
    <div class="splash-content">
        <div class="logo-container">
            <div class="logo"></div>
        </div>
        <div class="loading-text">
            <h1>IfcTester</h1>
            <p>Initializing environment...</p>
        </div>
        <div class="spinner-container">
            <div class="spinner"></div>
        </div>
    </div>
</div>

<style>
    .splash-screen {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        background: #00000059;
    }

    .splash-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2rem;
        text-align: center;
        background: #2b2d2b;
        padding: 50px 50px;
        border-radius: 50px;
        box-shadow: 0px 1px 5px #00000040;
        min-width: 400px;
    }

    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        background: #ffffff08;
        border-radius: 50%;
        border: 1px solid #ffffff1a;
    }

    .logo {
        background: url(/logo.svg);
        height: 64px;
        width: 64px;
        background-size: contain;
        background-position: center;
        background-repeat: no-repeat;
    }

    .loading-text h1 {
        margin: 0 0 0.5rem 0;
        font-size: 2.5rem;
        font-weight: 400;
        color: #ffffff;
        letter-spacing: -0.025em;
    }

    .loading-text p {
        margin: 0;
        font-size: 1rem;
        color: #b0b0b0;
        font-weight: 400;
    }

    .spinner-container {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .spinner {
        width: 32px;
        height: 32px;
        border: 3px solid #ffffff20;
        border-top: 3px solid #ffffff80;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        from { 
            transform: rotate(0deg); 
        }
        to { 
            transform: rotate(360deg); 
        }
    }
</style>