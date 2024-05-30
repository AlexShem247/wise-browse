function Controller() {
    installer.installationFinished.connect(function() {
        gui.clickButton(buttons.NextButton);
    });
}

function Component() {
    var page = gui.pageWidgetByObjectName("LicenseAgreementPage");
    if (page != null) {
        page.AcceptLicenseRadioButton.setChecked(true);
    }
}
